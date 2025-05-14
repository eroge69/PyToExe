# -*- coding: utf-8 -*-
"""
Smart PDF Searcher (ZIP Edition - File Output):
Finds a keyword phrase (from keyword.txt) within PDF files located inside
ZIP archives (in zip_files folder). Ranks results by relevance.
Outputs only the formatted results or critical errors to 'result.txt'.
"""

import fitz  # PyMuPDF
import os
import re
import unicodedata
from pathlib import Path
import math
import nltk
import zipfile
import io
import sys # To exit the script on critical errors

# --- NLTK Setup ---
# Attempt to import and initialize NLTK components.
# Errors during NLTK data loading are handled later.
try:
    from nltk.stem import WordNetLemmatizer
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    nltk_available = True
    # Initialize lemmatizer and stopwords here to catch potential LookupErrors early
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
except ImportError:
    nltk_available = False
    # Warning will be written to result.txt if NLTK fails later
except LookupError as e:
    # Specific data is missing (e.g., 'wordnet', 'stopwords', 'punkt')
    nltk_available = False
    # Store the error message to potentially write to file later
    nltk_error_message = f"NLTK data missing: {e}. Please download using nltk.download(...)."

# --- General Settings ---
ZIP_FOLDER_NAME = "zip_files"
KEYWORD_FILE_NAME = "keyword.txt"
RESULT_FILE_NAME = "result.txt" # Output file name
CONTEXT_BUFFER = 80
HIGHLIGHT_TAG_START = "<b>"
HIGHLIGHT_TAG_END = "</b>"
FIRST_PAGES_THRESHOLD = 3
HEADING_START_LINE_THRESHOLD = 15
HEADING_MAX_PREFIX_CHARS = 10

# --- Priority Levels ---
PRIORITY = {
    "FILENAME": 1,
    "FIRST_PAGE_EXACT": 2,
    "EXACT_MATCH": 4,
    "ALL_KEYWORDS_PROXIMITY": 5,
    "NOT_FOUND": float('inf')
}

# --- Helper Functions ---

def write_error_and_exit(filename, message):
    """Writes an error message to the result file and exits."""
    try:
        with open(filename, 'w', encoding='utf-8') as errfile:
            errfile.write(f"ERROR: {message}\n")
        print(f"Critical error occurred. Check '{filename}' for details.") # Info for console user
    except Exception as e:
        print(f"Critical error: {message}")
        print(f"Additionally, failed to write error to '{filename}': {e}")
    sys.exit(1) # Exit with a non-zero status code indicating an error

def read_keyword(filename):
    """Reads the keyword phrase from the first line of a text file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            keyword = f.readline().strip()
            if not keyword:
                return None, "Keyword file is empty or first line is blank."
            return keyword, None # Return keyword and no error
    except FileNotFoundError:
        return None, f"Keyword file '{filename}' not found."
    except Exception as e:
        return None, f"Error reading keyword file '{filename}': {e}"

def clean_snippet(text_snippet):
    """Cleans text snippet."""
    cleaned = text_snippet.replace('\n', ' ').strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned

def normalize_text(text):
    """Normalizes text using NFKD and converts to lowercase."""
    try:
        return unicodedata.normalize('NFKD', text).lower()
    except TypeError:
        return text.lower()

def get_lemmatized_tokens(text):
    """Gets lemmatized tokens, returns empty set on NLTK failure."""
    if not nltk_available or not text: return set()
    try:
        normalized = normalize_text(text)
        tokens = word_tokenize(normalized)
        lemmas = {
            lemmatizer.lemmatize(token) for token in tokens
            if token.isalnum() and token not in stop_words and len(token) > 1
        }
        return lemmas
    except LookupError as e: # Catch data errors specifically during usage
        global nltk_error_message # Access the global error message
        nltk_error_message = f"NLTK data missing during processing: {e}. Please download."
        # Fallback or indicate failure
        return set() # Indicate failure by returning empty set
    except Exception: # Catch other potential NLTK errors
        return set() # Indicate failure

def get_lemmatized_tokens_with_indices(text):
    """Gets lemmatized tokens with indices, returns empty list on NLTK failure."""
    tokens_indices = []
    if not nltk_available or not text: return tokens_indices
    try:
        normalized = normalize_text(text)
        for match in re.finditer(r'\b\w+\b', normalized):
            token = match.group(0)
            if token.isalnum() and token not in stop_words and len(token) > 1:
                lemma = lemmatizer.lemmatize(token)
                tokens_indices.append({'lemma': lemma, 'start': match.start(), 'end': match.end()})
        return tokens_indices
    except LookupError as e:
        global nltk_error_message
        nltk_error_message = f"NLTK data missing during processing: {e}. Please download."
        return []
    except Exception:
        return []

# --- Main Smart Search Function ---
def smart_search_zip_archives(zip_directory_path, keyword_phrase, context_chars):
    """
    Searches PDFs within ZIPs, returns findings or None on critical NLTK error during init.
    """
    all_findings = []
    # NLTK check - if it failed critically during init, report it
    if not nltk_available and 'nltk_error_message' in globals():
         write_error_and_exit(RESULT_FILE_NAME, nltk_error_message)


    # --- Process Keyword Phrase ---
    normalized_keyword_phrase = normalize_text(keyword_phrase)
    if not normalized_keyword_phrase:
         # This is unlikely if read_keyword worked, but handle it
         write_error_and_exit(RESULT_FILE_NAME, "Keyword phrase became empty after normalization.")

    search_lemmas = get_lemmatized_tokens(keyword_phrase)
    # If NLTK failed during get_lemmatized_tokens, use fallback
    if not search_lemmas and not nltk_available:
        search_lemmas = {normalized_keyword_phrase}
    elif not search_lemmas and nltk_available and 'nltk_error_message' in globals():
         # NLTK failed during lemma processing
         write_error_and_exit(RESULT_FILE_NAME, nltk_error_message)


    zip_files = list(zip_directory_path.glob('*.zip'))
    if not zip_files:
        # No ZIP files is not a critical error, just means no results. Return empty list.
        return all_findings

    # --- Loop through ZIP archives (Silently) ---
    for zip_path in zip_files:
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for item_name in zip_ref.namelist():
                    if item_name.lower().endswith('.pdf'):
                        pdf_filename_in_zip = os.path.basename(item_name)

                        # --- P1: Check PDF Filename ---
                        pdf_filename_lemmas = get_lemmatized_tokens(Path(pdf_filename_in_zip).stem)
                        if search_lemmas and pdf_filename_lemmas and search_lemmas.issubset(pdf_filename_lemmas):
                            all_findings.append({
                                'zip_filename': zip_path.name, 'filename': pdf_filename_in_zip, 'page': 0,
                                'priority': PRIORITY['FILENAME'], 'match_type': 'Keywords in PDF Filename', 'span': 0,
                                'context': f"Keywords found in PDF filename.",
                                'raw_snippet': pdf_filename_in_zip, 'matched_text': keyword_phrase
                            })

                        # --- Read and Process PDF Content ---
                        try:
                            pdf_bytes = zip_ref.read(item_name)
                            pdf_stream = io.BytesIO(pdf_bytes)
                            doc = fitz.open(stream=pdf_stream, filetype="pdf")
                        except Exception:
                            # Silently skip PDFs that cannot be opened/read from ZIP
                            continue

                        pages_with_exact_match = set()
                        for page_num, page in enumerate(doc):
                            # (Page processing logic: P2, P4, P5 - remains the same as previous version)
                            # Important: Ensure zip_filename is added to findings dicts.
                            # Errors within page processing should ideally be skipped silently too.
                            try:
                                page_text = page.get_text("text")
                                if not page_text: continue
                                normalized_page_text = normalize_text(page_text)
                                current_page_num = page_num + 1
                                match_found_this_page = False

                                # P2 & P4: Exact Phrase Match
                                start_index = 0
                                while True:
                                    index = normalized_page_text.find(normalized_keyword_phrase, start_index)
                                    if index == -1: break
                                    match_found_this_page = True
                                    pages_with_exact_match.add(current_page_num)
                                    current_priority = PRIORITY['FIRST_PAGE_EXACT'] if current_page_num <= FIRST_PAGES_THRESHOLD else PRIORITY['EXACT_MATCH']
                                    match_type_str = "Exact Match (First Pages)" if current_page_num <= FIRST_PAGES_THRESHOLD else "Exact Match"

                                    # Context calculation (incl. heading check)
                                    original_text_lower = page_text.lower()
                                    first_word_norm = normalized_keyword_phrase.split(' ', 1)[0]
                                    approx_start_orig = original_text_lower.find(first_word_norm, max(0, index - 20))
                                    if approx_start_orig == -1: approx_start_orig = index
                                    estimated_end_orig = approx_start_orig + len(normalized_keyword_phrase) + 15
                                    potential_match_zone = page_text[approx_start_orig:estimated_end_orig]
                                    actual_match_obj = re.search(re.escape(keyword_phrase), potential_match_zone, re.IGNORECASE)
                                    actual_matched_text = actual_match_obj.group(0) if actual_match_obj else keyword_phrase
                                    match_start_in_original = approx_start_orig
                                    if actual_match_obj: match_start_in_original += actual_match_obj.start()

                                    is_potential_heading = False
                                    prefix = ""
                                    context_start = match_start_in_original
                                    last_newline_pos = page_text.rfind('\n', 0, match_start_in_original)
                                    start_of_line_pos = 0 if last_newline_pos == -1 else last_newline_pos + 1
                                    text_before_match_on_line = page_text[start_of_line_pos:match_start_in_original]
                                    if not (match_start_in_original - start_of_line_pos <= HEADING_START_LINE_THRESHOLD and
                                            len(text_before_match_on_line.strip()) <= HEADING_MAX_PREFIX_CHARS):
                                        context_start = max(0, match_start_in_original - context_chars)
                                        prefix = "..." if context_start > 0 else ""

                                    context_end = min(len(page_text), match_start_in_original + len(actual_matched_text) + context_chars)
                                    suffix = "..." if context_end < len(page_text) else ""
                                    snippet_raw = page_text[context_start:context_end]
                                    snippet_clean = clean_snippet(snippet_raw)

                                    all_findings.append({
                                        'zip_filename': zip_path.name, 'filename': pdf_filename_in_zip, 'page': current_page_num,
                                        'priority': current_priority, 'match_type': match_type_str, 'span': 0,
                                        'context': f"{prefix}{snippet_clean}{suffix}".strip().replace(" ...","...").replace("... ","..."),
                                        'raw_snippet': snippet_clean, 'matched_text': actual_matched_text
                                    })
                                    start_index = index + 1

                                # P5: All Keywords Present
                                if not match_found_this_page and search_lemmas:
                                    page_lemmas_with_indices = get_lemmatized_tokens_with_indices(page_text)
                                    page_lemmas_set = {token['lemma'] for token in page_lemmas_with_indices}
                                    if search_lemmas.issubset(page_lemmas_set):
                                        # (Logic for P5 context and span calculation)
                                        min_pos = float('inf'); max_pos = float('-inf'); first_kw_match_info = None
                                        found_indices = []; required_lemmas_found_on_page = set()
                                        for token_info in page_lemmas_with_indices:
                                            if token_info['lemma'] in search_lemmas:
                                                found_indices.append(token_info['start'])
                                                required_lemmas_found_on_page.add(token_info['lemma'])
                                                if first_kw_match_info is None: first_kw_match_info = token_info
                                        if required_lemmas_found_on_page == search_lemmas and found_indices: span = max(found_indices) - min(found_indices)
                                        else: span = float('inf')

                                        context_snippet = f"All keywords found on page."; raw_snippet_context = context_snippet
                                        matched_text_for_highlight = first_kw_match_info['lemma'] if first_kw_match_info else list(search_lemmas)[0]
                                        if first_kw_match_info:
                                            approx_start_orig_kw = first_kw_match_info['start']
                                            potential_kw_zone = page_text[approx_start_orig_kw : approx_start_orig_kw + len(matched_text_for_highlight) + 15] # Increased buffer slightly
                                            actual_kw_match_obj = None
                                            try: # Try to find original casing
                                                actual_kw_match_obj = re.search(re.escape(matched_text_for_highlight), potential_kw_zone, re.IGNORECASE)
                                                if actual_kw_match_obj: matched_text_for_highlight = actual_kw_match_obj.group(0)
                                            except re.error: pass # Ignore if regex fails on lemma
                                            context_start_kw = max(0, approx_start_orig_kw - context_chars)
                                            prefix_kw = "..." if context_start_kw > 0 else ""
                                            context_end_kw = min(len(page_text), approx_start_orig_kw + len(matched_text_for_highlight) + context_chars)
                                            suffix_kw = "..." if context_end_kw < len(page_text) else ""
                                            snippet_raw_kw = page_text[context_start_kw:context_end_kw]
                                            snippet_clean_kw = clean_snippet(snippet_raw_kw)
                                            context_snippet = f"{prefix_kw}{snippet_clean_kw}{suffix_kw}".strip().replace(" ...","...").replace("... ","...")
                                            raw_snippet_context = snippet_clean_kw

                                        all_findings.append({
                                            'zip_filename': zip_path.name, 'filename': pdf_filename_in_zip, 'page': current_page_num,
                                            'priority': PRIORITY['ALL_KEYWORDS_PROXIMITY'], 'match_type': 'All Keywords on Page', 'span': span,
                                            'context': context_snippet, 'raw_snippet': raw_snippet_context,
                                            'matched_text': matched_text_for_highlight
                                        })
                            except Exception:
                                # Silently skip page processing errors
                                continue
                        doc.close()
        except zipfile.BadZipFile:
            # Silently skip bad zip files
            continue
        except Exception:
            # Silently skip other ZIP processing errors
            continue

    # --- Final Sorting ---
    all_findings.sort(key=lambda x: (
        x['priority'],
        x.get('span', 0) if x['priority'] == PRIORITY['ALL_KEYWORDS_PROXIMITY'] else 0,
        x.get('zip_filename', ''),
        x['filename'],
        x['page']
    ))
    return all_findings

# --- Main Execution Block ---
if __name__ == "__main__":
    current_working_directory = Path(os.getcwd())
    zip_dir = current_working_directory / ZIP_FOLDER_NAME
    keyword_file_path = current_working_directory / KEYWORD_FILE_NAME
    result_file_path = current_working_directory / RESULT_FILE_NAME

    # 1. Read Keyword
    search_term, error = read_keyword(keyword_file_path)
    if error:
        write_error_and_exit(result_file_path, error)
    if not search_term: # Handle case where read_keyword returns None without error str
         write_error_and_exit(result_file_path,"Failed to read a valid keyword.")


    # 2. Check ZIP Directory Exists
    if not zip_dir.is_dir():
        write_error_and_exit(result_file_path, f"ZIP directory '{ZIP_FOLDER_NAME}' not found in the current location.")

    # 3. Perform Search
    final_results = smart_search_zip_archives(zip_dir, search_term, CONTEXT_BUFFER)

    # 4. Write Results or 'Not Found' to File
    try:
        with open(result_file_path, 'w', encoding='utf-8') as outfile:
            if final_results:
                for i, finding in enumerate(final_results): # No start=1 needed for internal logic
                    full_context_from_finding = finding['context']
                    text_to_highlight = finding['matched_text']
                    highlighted_context = full_context_from_finding # Default

                    # Apply highlighting
                    try:
                        # Use non-capturing group and IGNORECASE
                        highlighted_context = re.sub(
                            f"({re.escape(text_to_highlight)})",
                            f"{HIGHLIGHT_TAG_START}\\1{HIGHLIGHT_TAG_END}",
                            full_context_from_finding,
                            count=1, flags=re.IGNORECASE
                        )
                    except (re.error, TypeError):
                        pass # Keep default context if regex fails

                    # Write formatted result lines
                    if finding['page'] > 0: # Standard match
                        outfile.write(f"zip_file_name[{i+1}]$ = '{finding['zip_filename']}'\n")
                        outfile.write(f"pdf_file_name[{i+1}]$ = '{finding['filename']}'\n")
                    else: # Filename match
                        outfile.write(f"zip_file_name[{i+1}]$ = '{finding['zip_filename']}'\n") # Still show zip
                        outfile.write(f"pdf_file_name[{i+1}]$ = '{finding['filename']}'\n")

                    outfile.write(f"Page_number[{i+1}]$ = '{finding['page']}'\n")
                    outfile.write(f"Result_Text[{i+1}]$ = '{highlighted_context}'\n")
                    # Add newline separator between results
                    if i < len(final_results) - 1:
                         outfile.write("\n")

            else:
                # No results found - write nothing as per requirement for clean output
                # If you want a "not found" message, uncomment the next line
                # outfile.write(f"No results found for '{search_term}'.\n")
                pass # Keep file empty if no results

        # Optional: Print success message to console
        # print(f"Search complete. Results (if any) written to '{result_file_path}'.")

    except Exception as e:
        # Handle potential errors during file writing
        print(f"Error writing results to file '{result_file_path}': {e}")