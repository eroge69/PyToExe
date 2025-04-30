import sys
import json
import os

def extract_texts_from_json(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        messages = data.get("messages", [])
        texts = [msg.get("text", "") for msg in messages if "text" in msg]

        # Create output .txt file in same directory
        base_name = os.path.splitext(json_path)[0]
        output_path = base_name + "_extracted.txt"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(texts))

        print(f"Extracted {len(texts)} messages to {output_path}")
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Drag and drop a JSON file onto this .exe")
        input("Press Enter to exit...")
        sys.exit(1)

    json_path = sys.argv[1]
    extract_texts_from_json(json_path)
    input("Done. Press Enter to exit...")
