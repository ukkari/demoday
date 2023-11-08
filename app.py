from flask import Flask, request, jsonify
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import base64
import os
import re

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


app = Flask(__name__)
load_dotenv()

@app.route('/demoday', methods=['POST'])
def demo_day():
    now = datetime.now()
    target_date = datetime(now.year, 11, 3)
    
    # If today's date is past November 3rd, calculate time until November 3rd of next year
    if now > target_date:
        target_date = datetime(now.year + 1, 11, 3)
    
    delta = target_date - now
    response_text = f'11/3までの残り日数: {delta.days+1} 日'
    
    return jsonify({"response_type": "in_channel", "text": response_text})

@app.route('/gpt4v', methods=['POST'])
def gpt4v():
    image_url = "https://jr.mitou.org/assets/img/404.webp"
    auth_header = request.headers.get('Authorization')
    if auth_header:
        token = auth_header.split(" ")[1]
        if token != os.getenv("BEARER_TOKEN"):
            response_text = "invalid token"
            return jsonify({"response_type": "in_channel", "text": response_text})
        else:
            inputs = request.form.get('text').split()
            print(request)
            print(request.files)
            if 'file' in request.files:
                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    mime_type = f"image/{filename.rsplit('.', 1)[1].lower()}"
                    # Read file data and encode it
                    image_data = file.read()
                    base64_image = base64.b64encode(image_data).decode('utf-8')
                    image_payload = {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}"
                        }
                    }
                    prompt_text = " ".join(inputs[0:])
                else:
                    response_text = "invalid input"
                    return jsonify({"response_type": "in_channel", "text": response_text})
            else:
                if len(inputs) < 2 or not inputs[0].startswith("http"):
                    response_text = "invalid input"
                    return jsonify({"response_type": "in_channel", "text": response_text})
                else:
                    image_url = inputs[0]
                    image_payload = {
                        "type": "image_url",
                        "image_url": image_url
                    }
                    prompt_text = " ".join(inputs[1:])

            client = OpenAI(
                # defaults to os.environ.get("OPENAI_API_KEY")
            )

            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            image_payload,
                        ],
                    }
                ],
                max_tokens=500,
            )
            response_text_raw = response.choices[0].message.content
            response_text = f"** prompt **: {prompt_text}\n** response **: {response_text_raw}\n** image **: [![Image]({image_url})]({image_url})"
            print(response_text)
    else:
        response_text = "invalid token"
    return jsonify({"response_type": "in_channel", "text": response_text})
