from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/demoday', methods=['POST'])
def demo_day():
    now = datetime.now()
    target_date = datetime(now.year, 11, 3)
    
    # If today's date is past November 3rd, calculate time until November 3rd of next year
    if now > target_date:
        target_date = datetime(now.year + 1, 11, 3)
    
    delta = target_date - now
    response_text = f'Time remaining until November 3rd: {delta.days} days, {delta.seconds // 3600} hours, {(delta.seconds // 60) % 60} minutes.'
    
    return jsonify({"text": response_text})