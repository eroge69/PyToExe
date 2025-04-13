from flask import Flask, jsonify
import random
import string
import pandas as pd
from transformers import (
    GPT2Tokenizer, GPT2LMHeadModel,
    T5Tokenizer, T5ForConditionalGeneration,
    BartTokenizer, BartForConditionalGeneration,
    AutoTokenizer, AutoModelForCausalLM
)
import logging
import redis
import json
import threading
import time
from queue import Queue
import torch
import subprocess
import os
import signal
import platform
import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image
from licensing.models import *
from licensing.methods import Key, Helpers
import socket
import sys
import io
import atexit
import tkinter as tk
from tkinter import messagebox

# Redirect stdout and stderr for executable logging
if getattr(sys, 'frozen', False):
    log_file = os.path.join(os.path.dirname(sys.executable), 'app_output.log')
    sys.stdout = open(log_file, 'w')
    sys.stderr = sys.stdout

# Set up logging
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Path handling for bundled resources
base_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))

def resource_path(relative_path):
    try:
        full_path = os.path.join(base_path, relative_path)
        logging.debug(f"Accessing resource: {full_path}")
        return full_path
    except Exception as e:
        logging.error(f"Error accessing resource {relative_path}: {str(e)}")
        raise

BG_IMAGE_PATH = resource_path("redis_bin\Digi-aigenerator-jpg.jpg")
pubKey = "<RSAKeyValue><Modulus>ox1g+RwNr+XitST0tu+uC+C45xgIYNh1b0Lnh8s3l8fsgadTDxoaQRMbTeAvYal0AMJn2E+6ShdSc0EZxEOF8pUNtBmphH1sLX7sWraWZYE9T5r/whrZrhAMNX53b7labpdBnXqoXXSjHq7JJgoP2wkNfZlZYWWz3+KxFUk9q+EJFaCaq5ZcJQZUQ9ST7bxDDkV62JqO3blAs9KZ4aZrBGWAE+OqcPKWLxqqfn5bl0MHWXQU8SeMM1z/P/NqSeMTdZM2YdPu14WKntT5/3XWU3k71arQWAh3+oyEeVtBCgTTCv6RtavShVsKbpqhK1nkvZXwzrm6LG8NiQ+6tgscAQ==</Modulus><Exponent>AQAB</Exponent></RSAKeyValue>"
auth = "WyIxMDU4MDQyMjgiLCJWWXdEb05XSGRHNzJGSG1JdDhlZHpTZmNCb2JBdDRmR2YzNFAzZkwyIl0="
license_file = resource_path("licensefile.skm")
app = Flask(__name__)

REDIS_BIN_PATH = resource_path("redis_bin")
REDIS_SERVER_EXEC = os.path.join(REDIS_BIN_PATH, "redis-server.exe" if platform.system() == "Windows" else "redis-server")
REDIS_PORT = 6379
redis_process = None
redis_client = redis.Redis(host='localhost', port=REDIS_PORT, decode_responses=True)
redis_ready = threading.Event()

MODEL_OPTIONS = {
    1: ("DigiQuick", "distilgpt2", GPT2Tokenizer, GPT2LMHeadModel),
    2: ("DigiMaster", "gpt2", GPT2Tokenizer, GPT2LMHeadModel),
    3: ("DigiMega", "gpt2-xl", GPT2Tokenizer, GPT2LMHeadModel),
    4: ("DigiGiant", "facebook/bart-large", BartTokenizer, BartForConditionalGeneration),
    5: ("DigiMini", "sentence-transformers/all-MiniLM-L6-v2", AutoTokenizer, AutoModelForCausalLM),
    6: ("ShortGen", "t5-small", T5Tokenizer, T5ForConditionalGeneration)
}

DEFAULT_PARAMS = {
    "distilgpt2": {"max_length": 25, "temperature": 1.6, "top_p": 0.7, "repetition_penalty": 1.5},
    "gpt2": {"max_length": 25, "temperature": 1.6, "top_p": 0.7, "repetition_penalty": 1.5},
    "gpt2-xl": {"max_length": 25, "temperature": 1.6, "top_p": 0.7, "repetition_penalty": 1.5},
    "facebook/bart-large": {"max_length": 25, "temperature": 1.6, "top_p": 0.7, "repetition_penalty": 1.5},
    "sentence-transformers/all-MiniLM-L6-v2": {"max_length": 25, "temperature": 1.6, "top_p": 0.7, "repetition_penalty": 1.5},
    "t5-small": {"max_length": 25, "temperature": 1.6, "top_p": 0.7, "repetition_penalty": 1.5}
}

try:
    import torch
except ImportError as e:
    messagebox.showerror("Import Error", f"Missing dependency: {e}\n\nTry: pip install torch")
    sys.exit(1)

tokenizer = None
model = None
current_model_name = None
current_params = {}
subject_cache_key = "subject_cache"
body_cache_key = "body_cache"
generation_queue = Queue()
api_running = False

# Load CSV files
subjects_df = pd.read_csv(resource_path('aisubject.csv'))
all_words = subjects_df['subject'].dropna().tolist()
blocked_words = [word for row in subjects_df['blocked words'].dropna() for word in row.split()]

bodies_df = pd.read_csv(resource_path('aibody.csv'))
all_bodies = bodies_df.get('body', bodies_df.iloc[:, 0]).dropna().tolist()

# Blocked categories (shortened for brevity)
COUNTRY_NAMES = ["afghanistan", "albania", "algeria", "andorra", "angola"]
PORN_SEXUAL_TERMS = ["porn", "sex", "nude", "naked", "erotic"]
MILITARY_TERMS = ["army", "navy", "airforce", "marine", "soldier"]

def verify_license(product_key):
    result = Key.activate(token=auth, rsa_pub_key=pubKey, product_id=29460, key=product_key, machine_code=Helpers.GetMachineCode(v=2), friendly_name=socket.gethostname())
    if result[0] is None:
        return False, result[1]
    with open(license_file, 'w') as f:
        f.write(result[0].save_as_string())
    return True, result[0]

def license_prompt():
    root = ctk.CTk()
    root.title("License Activation")
    root.geometry("1024x600")
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    bg_image = Image.open(BG_IMAGE_PATH).resize((1280, 720), Image.LANCZOS)
    root.bg_image = CTkImage(light_image=bg_image, dark_image=bg_image, size=(1280, 720))
    ctk.CTkLabel(root, text="", image=root.bg_image).place(x=0, y=0, relwidth=1, relheight=1)

    frame = ctk.CTkFrame(root, width=400, height=300, corner_radius=15)
    frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    ctk.CTkLabel(frame, text="Activate Your License", font=("Arial", 20, "bold")).pack(pady=20)
    product_key_entry = ctk.CTkEntry(frame, width=300, placeholder_text="Enter your product key")
    product_key_entry.pack(pady=10)
    error_label = ctk.CTkLabel(frame, text="", text_color="red")
    error_label.pack(pady=10)

    def submit_key():
        success, response = verify_license(product_key_entry.get().strip())
        if success:
            show_main_gui(root)
        else:
            error_label.configure(text=f"Error: {response}")

    ctk.CTkButton(frame, text="Activate", command=submit_key).pack(pady=10)

    def on_close():
        global api_running
        api_running = False
        stop_redis_server()
        root.destroy()
        sys.exit(0)

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

def show_main_gui(root):
    global api_running
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Subject & Body Generator")
    root.geometry("1024x768")

    left_frame = ctk.CTkFrame(root, width=300, height=700, corner_radius=15)
    left_frame.pack(side=ctk.LEFT, padx=20, pady=20, fill=ctk.Y)

    ctk.CTkLabel(left_frame, text="Model & Parameters", font=("Arial", 20, "bold")).pack(pady=10)
    model_var = ctk.IntVar(value=0)
    ctk.CTkLabel(left_frame, text="Select Model:").pack(pady=5)
    for num, (custom_name, _, _, _) in MODEL_OPTIONS.items():
        ctk.CTkRadioButton(left_frame, text=custom_name, variable=model_var, value=num, command=lambda n=num: update_params(n)).pack(pady=5)

    param_frame = ctk.CTkFrame(left_frame)
    param_frame.pack(pady=10, fill=ctk.X, padx=10)

    max_length_subject_var = ctk.IntVar(value=25)
    max_length_body_var = ctk.IntVar(value=50)
    temperature_subject_var = ctk.DoubleVar(value=1.5)
    temperature_body_var = ctk.DoubleVar(value=1.5)
    top_p_subject_var = ctk.DoubleVar(value=0.8)
    top_p_body_var = ctk.DoubleVar(value=0.9)
    repetition_penalty_subject_var = ctk.DoubleVar(value=1.5)
    repetition_penalty_body_var = ctk.DoubleVar(value=1.5)

    def update_params(model_num):
        global current_params, current_model_name
        if model_num in MODEL_OPTIONS:
            _, model_name, _, _ = MODEL_OPTIONS[model_num]
            current_model_name = model_name
            current_params = {"subject": DEFAULT_PARAMS[model_name].copy(), "body": DEFAULT_PARAMS[model_name].copy()}
            max_length_subject_var.set(current_params["subject"]["max_length"])
            max_length_body_var.set(current_params["body"]["max_length"])
            temperature_subject_var.set(current_params["subject"]["temperature"])
            temperature_body_var.set(current_params["body"]["temperature"])
            top_p_subject_var.set(current_params["subject"]["top_p"])
            top_p_body_var.set(current_params["body"]["top_p"])
            repetition_penalty_subject_var.set(current_params["subject"]["repetition_penalty"])
            repetition_penalty_body_var.set(current_params["body"]["repetition_penalty"])

    params = [
        ("Max Length (Subject):", max_length_subject_var, "subject", "max_length"),
        ("Max Length (Body):", max_length_body_var, "body", "max_length"),
        ("HEAT (Subject): (0.0-2.0)", temperature_subject_var, "subject", "temperature"),
        ("HEAT (Body): (0.0-2.0)", temperature_body_var, "body", "temperature"),
        ("Precision (Subject): (0.00-0.99)", top_p_subject_var, "subject", "top_p"),
        ("Precision (Body): (0.00-0.99)", top_p_body_var, "body", "top_p"),
        ("Repetition Penalty (Subject): (0.0-2.0)", repetition_penalty_subject_var, "subject", "repetition_penalty"),
        ("Repetition Penalty (Body): (0.0-2.0)", repetition_penalty_body_var, "body", "repetition_penalty")
    ]

    for i, (label, var, category, key) in enumerate(params):
        ctk.CTkLabel(param_frame, text=label).grid(row=i, column=0, padx=5, pady=5)
        entry = ctk.CTkEntry(param_frame, textvariable=var, width=100)
        entry.grid(row=i, column=1, padx=5, pady=5)
        entry.bind("<KeyRelease>", lambda e, c=category, k=key, v=var: update_param(c, k, v.get()))

    def update_param(category, key, value):
        if current_model_name and key in current_params[category]:
            try:
                current_params[category][key] = float(value) if key != "max_length" else int(value)
            except ValueError:
                pass

    status_label = ctk.CTkLabel(left_frame, text="API Status: Stopped", text_color="red")
    status_label.pack(pady=10)

    def start_api():
        global api_running
        if model_var.get() == 0:
            status_label.configure(text="API Status: Please select a model", text_color="red")
            return
        if not api_running:
            api_running = True
            status_label.configure(text="API Status: Running", text_color="green")
            threading.Thread(target=start_flask_api, args=(model_var.get(),), daemon=True).start()

    ctk.CTkButton(left_frame, text="Start API", command=start_api).pack(pady=20)

    right_frame = ctk.CTkFrame(root, width=700, height=700, corner_radius=15)
    right_frame.pack(side=ctk.RIGHT, padx=20, pady=20, fill=ctk.BOTH, expand=True)

    subjects_frame = ctk.CTkFrame(right_frame, corner_radius=10)
    subjects_frame.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True, padx=5, pady=(5, 2.5))
    ctk.CTkLabel(subjects_frame, text="Generated Subjects", font=("Arial", 16, "bold")).pack(pady=5)
    global subjects_text
    subjects_text = ctk.CTkTextbox(subjects_frame, width=650, height=300, wrap="word")
    subjects_text.pack(pady=5, fill=ctk.BOTH, expand=True)
    subjects_text.configure(state="disabled")

    bodies_frame = ctk.CTkFrame(right_frame, corner_radius=10)
    bodies_frame.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True, padx=5, pady=(2.5, 5))
    ctk.CTkLabel(bodies_frame, text="Generated Bodies", font=("Arial", 16, "bold")).pack(pady=5)
    global bodies_text
    bodies_text = ctk.CTkTextbox(bodies_frame, width=650, height=300, wrap="word")
    bodies_text.pack(pady=5, fill=ctk.BOTH, expand=True)
    bodies_text.configure(state="disabled")

    def update_notifications():
        while True:
            try:
                redis_ready.wait()  # Wait for Redis to be ready
                cached_subjects = redis_client.lrange(subject_cache_key, 0, 99)
                subject_count = redis_client.llen(subject_cache_key)
                subjects_text.configure(state="normal")
                subjects_text.delete("1.0", ctk.END)
                if cached_subjects:
                    subjects = [json.loads(entry)["subject"] for entry in cached_subjects]
                    subjects_text.insert(ctk.END, f"Total Subjects: {subject_count}\n" + "\n".join(subjects))
                else:
                    subjects_text.insert(ctk.END, f"Total Subjects: {subject_count}\nNo subjects generated yet.")
                subjects_text.configure(state="disabled")

                cached_bodies = redis_client.lrange(body_cache_key, 0, 99)
                body_count = redis_client.llen(body_cache_key)
                bodies_text.configure(state="normal")
                bodies_text.delete("1.0", ctk.END)
                if cached_bodies:
                    bodies = [json.loads(entry)["body"] for entry in cached_bodies]
                    bodies_text.insert(ctk.END, f"Total Bodies: {body_count}\n" + "\n".join(bodies))
                else:
                    bodies_text.insert(ctk.END, f"Total Bodies: {body_count}\nNo bodies generated yet.")
                bodies_text.configure(state="disabled")

                print(f"Updated panels - Subjects: {subject_count}, Bodies: {body_count}")
            except redis.exceptions.ConnectionError as e:
                print(f"Redis connection error: {e}. Retrying in 5 seconds...")
                redis_ready.clear()
                time.sleep(5)
            except Exception as e:
                print(f"Error updating notifications: {e}")
            time.sleep(1)

    threading.Thread(target=update_notifications, daemon=True).start()

def monitor_redis():
    while api_running:
        try:
            if redis_client.ping():
                if not redis_ready.is_set():
                    print("Redis is now available")
                    redis_ready.set()
            else:
                redis_ready.clear()
                print("Redis not responding, restarting...")
                stop_redis_server()
                start_redis_server()
        except redis.exceptions.ConnectionError:
            redis_ready.clear()
            print("Redis connection lost, attempting restart...")
            stop_redis_server()
            start_redis_server()
        time.sleep(5)

def start_redis_server():
    global redis_process
    if not os.path.exists(REDIS_SERVER_EXEC):
        raise FileNotFoundError(f"redis-server not found at {REDIS_SERVER_EXEC}")
    try:
        redis_process = subprocess.Popen(
            [REDIS_SERVER_EXEC, "--port", str(REDIS_PORT), "--maxmemory", "512mb", "--maxmemory-policy", "noeviction"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if platform.system() == "Windows" else 0
        )
        for _ in range(20):  # Wait up to 20 seconds
            if redis_process.poll() is not None:
                error_output = redis_process.stderr.read().decode('utf-8')
                raise RuntimeError(f"Redis terminated prematurely: {error_output}")
            if redis_client.ping():
                print(f"Started redis-server on port {REDIS_PORT} with PID {redis_process.pid}")
                redis_ready.set()
                return
            time.sleep(1)
        error_output = redis_process.stderr.read().decode('utf-8')
        raise RuntimeError(f"Failed to start redis-server after 20 seconds: {error_output}")
    except Exception as e:
        print(f"Error starting Redis: {e}")
        raise

def stop_redis_server():
    global redis_process
    if redis_process and redis_process.poll() is None:
        if platform.system() == "Windows":
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(redis_process.pid)])
        else:
            os.kill(redis_process.pid, signal.SIGTERM)
        redis_process.wait()
        print("Stopped redis-server")
    redis_ready.clear()

def load_model(model_number):
    global tokenizer, model, current_model_name
    if model_number not in MODEL_OPTIONS:
        raise ValueError("Invalid model number")
    redis_ready.wait()  # Ensure Redis is ready before loading model
    _, model_name, tokenizer_class, model_class = MODEL_OPTIONS[model_number]
    if model_name == "t5-small":  # Extra delay for ShortGen
        time.sleep(2)  # Give Redis extra time to stabilize
    tokenizer = tokenizer_class.from_pretrained(model_name)
    model = model_class.from_pretrained(model_name)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id
    current_model_name = model_name
    return model_name

def filter_subject(subject):
    subject_lower = subject.lower()
    if len(subject) <= 5 or len(subject.split()) < 3:
        return False
    if any(word in subject_lower for word in blocked_words + COUNTRY_NAMES + PORN_SEXUAL_TERMS + MILITARY_TERMS):
        return False
    if any(char.isdigit() for char in subject_lower):
        return False
    return True

def generate_subject():
    if not tokenizer or not model:
        raise RuntimeError("Model not initialized")
    redis_ready.wait()
    input_text = "subject:" if current_model_name != "t5-small" else "generate subject:"
    inputs = tokenizer(input_text, return_tensors="pt", padding=True)
    output = model.generate(
        **inputs,
        pad_token_id=tokenizer.pad_token_id,
        max_length=current_params["subject"]["max_length"],
        do_sample=True,
        temperature=current_params["subject"]["temperature"],
        top_p=current_params["subject"]["top_p"],
        repetition_penalty=current_params["subject"]["repetition_penalty"],
        num_return_sequences=1
    )
    base_sentence = tokenizer.decode(output[0], skip_special_tokens=True).replace("subject:", "").strip()
    base_words = base_sentence.split()
    shuffled_phrases = all_words.copy()
    random.shuffle(shuffled_phrases)
    insert_phrase = shuffled_phrases[0].split()
    final_words = base_words[:1] + insert_phrase + base_words[1:] if len(base_words) > 2 else base_words + insert_phrase
    email_subject = " ".join([final_words[0].capitalize()] + final_words[1:]) + "."
    email_subject = ''.join(c for c in email_subject if c in string.ascii_letters + string.digits + " .,-'?!")
    while not filter_subject(email_subject):
        email_subject = generate_subject()["subject"]
    return {"subject": email_subject, "model_used": current_model_name}

def generate_body():
    if not tokenizer or not model:
        raise RuntimeError("Model not initialized")
    redis_ready.wait()
    input_text = "body:" if current_model_name != "t5-small" else "generate body:"
    inputs = tokenizer(input_text, return_tensors="pt", padding=True)
    output = model.generate(
        **inputs,
        pad_token_id=tokenizer.pad_token_id,
        max_length=current_params["body"]["max_length"],
        do_sample=True,
        temperature=current_params["body"]["temperature"],
        top_p=current_params["body"]["top_p"],
        repetition_penalty=current_params["body"]["repetition_penalty"],
        num_return_sequences=1
    )
    base_sentence = tokenizer.decode(output[0], skip_special_tokens=True).replace("body:", "").strip()
    base_words = base_sentence.split()
    shuffled_phrases = all_bodies.copy()
    random.shuffle(shuffled_phrases)
    insert_phrase = shuffled_phrases[0].split()
    final_words = base_words[:1] + insert_phrase + base_words[1:] if len(base_words) > 2 else base_words + insert_phrase
    email_body = " ".join([final_words[0].capitalize()] + final_words[1:]) + "."
    email_body = ''.join(c for c in email_body if c in string.ascii_letters + string.digits + " .,-'?!")
    while not filter_subject(email_body):
        email_body = generate_body()["body"]
    return {"body": email_body, "model_used": current_model_name}

def background_generator():
    while api_running:
        try:
            redis_ready.wait()
            with redis_client.pipeline() as pipe:
                for _ in range(10):
                    subject_data = generate_subject()
                    pipe.lpush(subject_cache_key, json.dumps(subject_data))
                    body_data = generate_body()
                    pipe.lpush(body_cache_key, json.dumps(body_data))
                pipe.ltrim(subject_cache_key, 0, 19999)
                pipe.ltrim(body_cache_key, 0, 19999)
                pipe.execute()
            time.sleep(2)
        except Exception as e:
            print(f"Error in background generator: {e}")
            time.sleep(5)

@app.route('/generate', methods=['GET'])
def api_generate():
    redis_ready.wait()
    cached_subject = redis_client.rpop(subject_cache_key)
    subject_data = json.loads(cached_subject) if cached_subject else generate_subject()
    return jsonify({"subjects": subject_data})

@app.route('/get_subject', methods=['GET'])
def get_subject():
    redis_ready.wait()
    cached = redis_client.rpop(subject_cache_key)
    subject_data = json.loads(cached) if cached else generate_subject()
    return jsonify({"subject": subject_data["subject"], "model_used": subject_data["model_used"]})

@app.route('/get_body', methods=['GET'])
def get_body():
    redis_ready.wait()
    cached = redis_client.rpop(body_cache_key)
    body_data = json.loads(cached) if cached else generate_body()
    return jsonify({"body": body_data["body"], "model_used": body_data["model_used"]})

@app.route('/cached_subjects', methods=['GET'])
def get_cached_subjects():
    redis_ready.wait()
    cached_data = redis_client.lrange(subject_cache_key, 0, -1)
    subjects = [json.loads(entry) for entry in cached_data]
    return jsonify({"cached_subjects": subjects})

@app.route('/cached_bodies', methods=['GET'])
def get_cached_bodies():
    redis_ready.wait()
    cached_data = redis_client.lrange(body_cache_key, 0, -1)
    bodies = [json.loads(entry) for entry in cached_data]
    return jsonify({"cached_bodies": bodies})

def cleanup():
    stop_redis_server()
    print("Application cleanup completed.")

atexit.register(cleanup)

def start_flask_api(selected_model):
    global api_running
    try:
        start_redis_server()
        threading.Thread(target=monitor_redis, daemon=True).start()
        print(f"Loading model: {load_model(selected_model)}")
        threading.Thread(target=background_generator, daemon=True).start()
        app.run(debug=False, threaded=True)
    except Exception as e:
        print(f"Error in Flask API: {e}")
        api_running = False
        stop_redis_server()

if __name__ == "__main__":
    if os.path.exists(license_file):
        with open(license_file, 'r') as f:
            license_key = LicenseKey.load_from_string(pubKey, f.read())
            if Helpers.IsOnRightMachine(license_key):
                license_prompt()
            else:
                try:
                    os.remove(license_file)
                    print("Deleted invalid license file.")
                except Exception as e:
                    print(f"Failed to delete license file: {e}")
                license_prompt()
    else:
        license_prompt()