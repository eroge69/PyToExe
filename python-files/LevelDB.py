import json
import leveldb
import sys
import os

def convert_leveldb_to_json(leveldb_path, output_json_path):
    try:
        # اتصال به LevelDB
        db = leveldb.LevelDB(leveldb_path)
        
        # خواندن تمام کلیدها و مقادیر
        data = {}
        for key, value in db.RangeIter():
            try:
                # تبدیل بایت به رشته (اگر داده متنی است)
                key_str = key.decode('utf-8')
                value_str = value.decode('utf-8')
            except UnicodeDecodeError:
                # اگر داده باینری است، به فرمت Hex نمایش داده می‌شود
                key_str = key.hex()
                value_str = value.hex()
            data[key_str] = value_str
        
        # ذخیره به صورت JSON
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        print(f"Data successfully saved to {output_json_path}")
        return True
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: leveldb_to_json.exe <leveldb_path> <output_json_path>")
        sys.exit(1)
    
    leveldb_path = sys.argv[1]
    output_json_path = sys.argv[2]
    convert_leveldb_to_json(leveldb_path, output_json_path)