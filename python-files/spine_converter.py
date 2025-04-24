import json
import sys
import os

def main(json_path):
    try:
        # Get the directory of the JSON file
        json_dir = os.path.dirname(json_path)
        print(f"JSON file directory: {json_dir}")

        # Read the JSON file
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("JSON file loaded")

        # Extract atlas data and write to file
        atlas_asset = next(item for item in data if item['Type'] == 'SpineAtlasAsset')
        atlas_text = atlas_asset['Properties']['rawData']
        atlas_file = os.path.join(json_dir, 'c_changli_1.atlas')
        with open(atlas_file, 'w', encoding='utf-8') as f:
            f.write(atlas_text)
        print(f"Atlas file written: {atlas_file}")

        # Extract skel data and write to file
        skel_asset = next(item for item in data if item['Type'] == 'SpineSkeletonDataAsset')
        skel_data = skel_asset['Properties']['rawData']
        skel_file = os.path.join(json_dir, 'c_changli_1.skel')
        with open(skel_file, 'wb') as f:
            f.write(bytearray(skel_data))
        print(f"Skel file written: {skel_file}")

        print("Script execution completed")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please drag and drop a JSON file onto the EXE")
    else:
        json_path = sys.argv[1]
        main(json_path)