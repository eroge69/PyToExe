import argparse
import os
import xml.etree.ElementTree as ET
from xml_processor import parse_xml_file # Assuming this function is well-defined
from translation_engine import TranslationEngine
from glossary_manager import GlossaryManager

def create_output_xml_tree(original_root_tag, original_root_attrib, translated_data):
    """Creates an XML tree from translated data, preserving original root tag and attributes."""
    new_root = ET.Element(original_root_tag, original_root_attrib)
    for item in translated_data:
        content_element = ET.SubElement(new_root, "content", 
                                        contentuid=item["uid"], 
                                        version=item["version"])
        content_element.text = item["translated_text"]
    return ET.ElementTree(new_root)

def main():
    parser = argparse.ArgumentParser(description="Translate Baldur's Gate 3 XML localization files.")
    parser.add_argument("input_path", help="Path to the input XML file or directory containing XML files.")
    parser.add_argument("output_path", help="Path to the directory to save translated XML files.")
    parser.add_argument("--glossary", help="Optional path to a JSON glossary file.", default=None)
    parser.add_argument("--model_name", help="Optional Hugging Face model name for translation.", default=None)
    # Add more arguments as needed, e.g., for language pairs if the engine is generic

    args = parser.parse_args()

    # Initialize components
    print("Initializing Translation Program...")
    glossary_manager = GlossaryManager(args.glossary)
    # Pass model_name from args to TranslationEngine if provided
    translation_engine = TranslationEngine(model_name=args.model_name)

    if not translation_engine.translator:
        print("Failed to initialize translation engine. Exiting.")
        return

    if not os.path.exists(args.output_path):
        try:
            os.makedirs(args.output_path)
            print(f"Created output directory: {args.output_path}")
        except OSError as e:
            print(f"Error creating output directory {args.output_path}: {e}")
            return

    files_to_process = []
    if os.path.isfile(args.input_path) and args.input_path.endswith(".xml"):
        files_to_process.append(args.input_path)
    elif os.path.isdir(args.input_path):
        for filename in os.listdir(args.input_path):
            if filename.endswith(".xml"):
                files_to_process.append(os.path.join(args.input_path, filename))
    else:
        print(f"Error: Input path {args.input_path} is not a valid XML file or directory.")
        return

    if not files_to_process:
        print(f"No XML files found in {args.input_path}.")
        return

    print(f"Found {len(files_to_process)} XML file(s) to process.")

    for file_path in files_to_process:
        print(f"\nProcessing file: {file_path}")
        
        # Store original root tag and attributes
        original_root_tag = "contentList" # Default, can be read from original file
        original_root_attrib = {}       # Default, can be read from original file
        try:
            original_tree = ET.parse(file_path)
            original_root = original_tree.getroot()
            original_root_tag = original_root.tag
            original_root_attrib = original_root.attrib
        except Exception as e:
            print(f"Warning: Could not parse original XML to get root details for {file_path}: {e}. Using defaults.")


        parsed_data = parse_xml_file(file_path)
        if not parsed_data:
            print(f"No translatable content found or error parsing {file_path}. Skipping.")
            continue

        texts_for_ai = []
        for item in parsed_data:
            processed_text = glossary_manager.apply_glossary_to_text(item["text"])
            texts_for_ai.append(processed_text)
        
        print(f"Translating {len(texts_for_ai)} text segments...")
        # Using batch translation for efficiency
        raw_translated_texts = translation_engine.translate_batch(texts_for_ai)

        if not raw_translated_texts or len(raw_translated_texts) != len(parsed_data):
            print(f"Error during batch translation for {file_path}. Skipping.")
            continue

        final_translated_data = []
        for i, item in enumerate(parsed_data):
            if raw_translated_texts[i] is not None:
                final_text = glossary_manager.revert_glossary_placeholders(raw_translated_texts[i])
                final_translated_data.append({
                    "uid": item["uid"],
                    "version": item["version"],
                    "translated_text": final_text
                })
            else:
                print(f"Warning: Failed to translate segment UID {item['uid']} in {file_path}")
                # Optionally, include original text or a placeholder for failed translations
                final_translated_data.append({
                    "uid": item["uid"],
                    "version": item["version"],
                    "translated_text": item["text"] # Fallback to original text
                })

        # Create new XML tree and write to output file
        output_filename = os.path.basename(file_path)
        output_file_path = os.path.join(args.output_path, output_filename)
        
        try:
            translated_tree = create_output_xml_tree(original_root_tag, original_root_attrib, final_translated_data)
            # ET.indent is available in Python 3.9+ for pretty printing
            try:
                ET.indent(translated_tree.getroot(), space="  ", level=0)
            except AttributeError:
                print("Note: ET.indent for pretty XML output is not available in this Python version (requires 3.9+).")
            
            translated_tree.write(output_file_path, encoding="utf-8", xml_declaration=True)
            print(f"Translated file saved to: {output_file_path}")
        except Exception as e:
            print(f"Error writing translated XML to {output_file_path}: {e}")

    print("\nTranslation process completed.")

if __name__ == "__main__":
    main()

