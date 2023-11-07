from flask import Flask, request, jsonify
from datetime import datetime
from openai import OpenAI

app = Flask(__name__)

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
        if token != "nhjb64qd3jnbmfg1jpgtbqbeca":
            response_text = "invalid token"
        else:
            inputs = request.form.get('text').split()
            if len(inputs) < 2:
                response_text = "invalid input"
            else:
                image_url = inputs[0]
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
                                {
                                    "type": "image_url",
                                    "image_url": image_url,
                                },
                            ],
                        }
                    ],
                    max_tokens=500,
                )
                response_text = response.choices[0].message.content
                print(response_text)
    else:
        response_text = "invalid token"
    return jsonify({"response_type": "in_channel", "text": response_text, "attachments": {"image_url": image_url, "author_name": "GPT4V", "author_icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/GPT-4.png/480px-GPT-4.png"}})
