#!/usr/bin/env python3
"""
PDF Datasheet Downloader

This utility extracts URLs from an Excel spreadsheet column, 
searches each URL for datasheet PDF links, and downloads them to a local directory.
"""

import os
import re
import logging
import argparse
from pathlib import Path
from urllib.parse import urljoin, urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup
import trafilatura

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def is_valid_url(url):
    """Check if the URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def load_urls_from_excel(file_path, column_letter):
    """
    Load URLs from the specified column in an Excel file.
    
    Args:
        file_path: Path to the Excel file
        column_letter: Letter of the column containing URLs
    
    Returns:
        List of URLs
    """
    try:
        # Convert column letter to index (0-based)
        column_index = ord(column_letter.upper()) - ord('A')
        
        # Read the Excel file
        df = pd.read_excel(file_path, engine='openpyxl')
        
        # Check if column index is valid
        if column_index >= len(df.columns):
            logger.error(f"Column {column_letter} does not exist in the Excel file")
            return []
        
        # Extract URLs from the specified column
        urls = df.iloc[:, column_index].tolist()
        
        # Filter out invalid URLs and NaN values
        valid_urls = [url for url in urls if isinstance(url, str) and is_valid_url(url)]
        
        logger.info(f"Loaded {len(valid_urls)} valid URLs from column {column_letter}")
        return valid_urls
    
    except Exception as e:
        logger.error(f"Error loading Excel file: {e}")
        return []

def find_pdf_links(url):
    """
    Find PDF links on a webpage, prioritizing those containing 'datasheet'.
    
    Args:
        url: URL of the webpage to search
    
    Returns:
        List of PDF URLs found
    """
    pdf_links = []
    
    try:
        # Send a GET request to the URL
        logger.info(f"Searching for PDF links in {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all links on the page
        links = soup.find_all('a', href=True)
        
        # Find PDF links, prioritizing those with 'datasheet' in them
        datasheet_pdf_links = []
        other_pdf_links = []
        
        for link in links:
            href = link.get('href', '').lower()
            link_text = link.get_text().lower()
            
            # Skip non-PDF links
            if not (href.endswith('.pdf') or 'pdf' in href):
                continue
            
            # Construct absolute URL
            full_url = urljoin(url, href)
            
            # Prioritize links with 'datasheet' in the URL or text
            if 'datasheet' in href or 'datasheet' in link_text:
                datasheet_pdf_links.append(full_url)
            else:
                other_pdf_links.append(full_url)
        
        # Also try to find PDF links using regex (for cases where links might be in JavaScript or other elements)
        pdf_pattern = re.compile(r'(https?://[^\s"\'<>]+\.pdf)', re.IGNORECASE)
        datasheet_pattern = re.compile(r'(https?://[^\s"\'<>]+datasheet[^\s"\'<>]*\.pdf)', re.IGNORECASE)
        
        # Find datasheet PDFs with regex
        for match in datasheet_pattern.finditer(response.text):
            full_url = match.group(1)
            if full_url not in datasheet_pdf_links:
                datasheet_pdf_links.append(full_url)
        
        # Find other PDFs with regex
        for match in pdf_pattern.finditer(response.text):
            full_url = match.group(1)
            if full_url not in datasheet_pdf_links and full_url not in other_pdf_links:
                other_pdf_links.append(full_url)
        
        # Use trafilatura to extract text for better analysis
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            if text:
                # Look for patterns like "download datasheet" nearby PDF links
                lines = text.split('\n')
                for line in lines:
                    if 'datasheet' in line.lower():
                        # Look for URLs in this line
                        for match in pdf_pattern.finditer(line):
                            full_url = match.group(1)
                            if full_url not in datasheet_pdf_links:
                                datasheet_pdf_links.append(full_url)
        
        # Combine the results, prioritizing datasheet PDFs
        pdf_links = datasheet_pdf_links + other_pdf_links
        
        if pdf_links:
            logger.info(f"Found {len(pdf_links)} PDF links ({len(datasheet_pdf_links)} datasheet PDFs)")
        else:
            logger.warning(f"No PDF links found at {url}")
        
        return pdf_links
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error accessing URL {url}: {e}")
        return []
    except Exception as e:
        logger.error(f"Error processing URL {url}: {e}")
        return []

def download_pdf(url, output_dir):
    """
    Download a PDF file from the given URL.
    
    Args:
        url: URL of the PDF to download
        output_dir: Directory to save the PDF to
    
    Returns:
        Path to the downloaded file or None if download failed
    """
    try:
        logger.info(f"Downloading PDF from {url}")
        
        # Send a GET request to download the PDF
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
        
        # Check if content is actually a PDF
        content_type = response.headers.get('Content-Type', '').lower()
        if 'application/pdf' not in content_type and not url.lower().endswith('.pdf'):
            logger.warning(f"URL {url} does not point to a PDF file")
            return None
        
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract filename from URL or use a default name
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        
        if not filename or not filename.lower().endswith('.pdf'):
            filename = f"datasheet_{hash(url) % 10000}.pdf"
        
        # Make sure the filename is valid and unique
        safe_filename = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)
        if not safe_filename.lower().endswith('.pdf'):
            safe_filename += '.pdf'
        
        # Check if file already exists, append number if needed
        base_name = safe_filename[:-4]  # Remove .pdf
        counter = 1
        while os.path.exists(os.path.join(output_dir, safe_filename)):
            safe_filename = f"{base_name}_{counter}.pdf"
            counter += 1
        
        # Save the PDF file
        file_path = os.path.join(output_dir, safe_filename)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Successfully downloaded PDF to {file_path}")
        return file_path
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading PDF from {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error saving PDF from {url}: {e}")
        return None

def process_url(url, output_dir):
    """
    Process a single URL: find PDF links and download them.
    
    Args:
        url: URL to process
        output_dir: Directory to save PDFs to
    
    Returns:
        List of paths to downloaded files
    """
    downloaded_files = []
    
    # Find PDF links
    pdf_links = find_pdf_links(url)
    
    if not pdf_links:
        logger.warning(f"No PDF links found at {url}")
        return downloaded_files
    
    # Download each PDF
    for pdf_url in pdf_links:
        file_path = download_pdf(pdf_url, output_dir)
        if file_path:
            downloaded_files.append(file_path)
            # If we found and downloaded a datasheet PDF, we can stop
            if 'datasheet' in pdf_url.lower():
                break
    
    return downloaded_files

def main():
    """Main function to run the PDF datasheet downloader."""
    parser = argparse.ArgumentParser(description='Download PDF datasheets from URLs in an Excel file')
    parser.add_argument('excel_file', help='Path to the Excel file')
    parser.add_argument('column_letter', help='Letter of the column containing URLs')
    parser.add_argument('--output-dir', '-o', default='downloaded_datasheets',
                        help='Directory to save downloaded PDFs (default: downloaded_datasheets)')
    args = parser.parse_args()
    
    # Validate input
    if not os.path.exists(args.excel_file):
        logger.error(f"Excel file not found: {args.excel_file}")
        return 1
    
    if not re.match(r'^[A-Za-z]$', args.column_letter):
        logger.error(f"Invalid column letter: {args.column_letter}. Must be a single letter A-Z.")
        return 1
    
    # Load URLs from Excel file
    urls = load_urls_from_excel(args.excel_file, args.column_letter)
    
    if not urls:
        logger.error("No valid URLs found in the specified column")
        return 1
    
    # Process each URL
    total_downloaded = 0
    output_dir = Path(args.output_dir)
    
    logger.info(f"Starting download process for {len(urls)} URLs")
    logger.info(f"PDFs will be saved to {output_dir.absolute()}")
    
    for i, url in enumerate(urls, 1):
        logger.info(f"Processing URL {i}/{len(urls)}: {url}")
        downloaded_files = process_url(url, args.output_dir)
        total_downloaded += len(downloaded_files)
    
    # Summary
    logger.info(f"Download process completed")
    logger.info(f"Total URLs processed: {len(urls)}")
    logger.info(f"Total PDFs downloaded: {total_downloaded}")
    logger.info(f"Files saved to: {output_dir.absolute()}")
    
    return 0

if __name__ == "__main__":
    exit(main())
