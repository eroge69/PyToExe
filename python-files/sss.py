import os
import io
import time
import base64
import numpy as np
import re
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image, ImageSequence, ImageEnhance
from io import BytesIO

app = Flask(__name__)
CORS(app)

def process_image(image_path, output_path, new_width=150):
    img = Image.open(image_path).convert('RGB')
    img_array = np.array(img)

    non_white_rows = np.where(np.mean(img_array, axis=(1, 2)) < 250)[0]
    if len(non_white_rows) > 0:
        top = non_white_rows[0]
        bottom = non_white_rows[-1]
        img = img.crop((0, top, img.width, bottom))

    aspect_ratio = img.height / img.width
    new_height = int(new_width * aspect_ratio)
    img = img.resize((new_width, new_height), Image.LANCZOS)

    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)

    img_array = np.array(img)
    threshold = 200
    mask = img_array < threshold
    img_array[mask] = 0
    img_array[~mask] = 255

    img = Image.fromarray(img_array)
    img.save(output_path, 'PNG')

def clean_result_text(text):
    clean_text = re.sub(r'[^a-zA-Z0-9]', '', text)
    if len(clean_text) > 5:
        clean_text = re.sub(r'(.)\1+', r'\1', clean_text)
    return clean_text

def merge_gif_frames_average_from_base64(base64_string):
    gif_data = base64.b64decode(base64_string)
    gif_bytes = io.BytesIO(gif_data)
    gif = Image.open(gif_bytes)
    frames = [np.array(f.convert("RGB")).astype(np.float32) for f in ImageSequence.Iterator(gif)]

    if not frames:
        raise ValueError("لم يتم العثور على فريمات في الصورة.")

    avg_frame = np.mean(frames, axis=0).astype(np.uint8)
    result = Image.fromarray(avg_frame)
    result.save("mergedview.png")

@app.route('/d3mk', methods=['POST'])
def handle_xai_ai():
    try:
        start_time = time.time()

        data = request.get_json()
        if 'file' not in data:
            return jsonify({'error': 'يرجى إرسال المفتاح "file" في JSON'}), 400

        base64_string = data['file']
        merge_gif_frames_average_from_base64(base64_string)

        image_path = "mergedview.png"
        process_image(image_path, image_path)

        with open(image_path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode("utf-8")
        image_url = f"data:image/png;base64,{image_base64}"

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                            "detail": "high",
                        },
                    },
                    {
                        "type": "text",
                        "text": "اكتب الحروف فى الصوره بسرعه كبيره ولا تكتب اى حاجه اخرى سوى الحروف او الارقام وهما فى الاغلب 5 حروف وارقام",
                    },
                ],
            },
        ]

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer xai-66X3npncUaUi8qqRbfpnuIb5LXi94kucVPan0Z8CCYGgTHXzJisbKD5sX2JagiYMKkyGGJ7rPIpdcqmb"
        }

        data = {
            "model": "grok-2-vision-latest",
            "messages": messages,
            "stream": False,
            "temperature": 0.1
        }

        response = requests.post("https://api.x.ai/v1/chat/completions", json=data, headers=headers)

        elapsed_time = time.time() - start_time

        if response.status_code == 200:
            completion = response.json()
            recognized_text = completion['choices'][0]['message']['content'].strip()
            clean_text = clean_result_text(recognized_text)
            return jsonify({
                'ocr_result': clean_text,
                'message': 'تم إرسال الصورة بنجاح إلى XAI API ومعالجة النص.',
                'elapsed_time_sec': round(elapsed_time, 2)
            }), 200
        else:
            return jsonify({'error': f"حدث خطأ: {response.text}"}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2321)
