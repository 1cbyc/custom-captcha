from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont
import random
import string
import io
import redis
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Initialize Redis for session storage
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Initialize rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

def generate_captcha_text():
    """Generate a random CAPTCHA text."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def create_captcha_image(text):
    """Create a CAPTCHA image with the given text."""
    # Create a new image with a white background
    width = 200
    height = 80
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Add noise and lines
    for _ in range(8):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill='gray', width=2)
    
    # Add text with random positioning and rotation
    for i, char in enumerate(text):
        x = 20 + i * 30
        y = random.randint(10, 40)
        angle = random.randint(-30, 30)
        draw.text((x, y), char, fill='black', font=None, angle=angle)
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

@app.route('/generate-captcha', methods=['GET'])
@limiter.limit("10 per minute")
def generate_captcha():
    """Generate a new CAPTCHA challenge."""
    captcha_text = generate_captcha_text()
    session_id = request.args.get('session_id', '')
    
    if not session_id:
        return jsonify({'error': 'Session ID required'}), 400
    
    # Store CAPTCHA in Redis with 5-minute expiration
    redis_client.setex(
        f'captcha:{session_id}',
        timedelta(minutes=5),
        captcha_text
    )
    
    # Generate and return the image
    image = create_captcha_image(captcha_text)
    return send_file(
        image,
        mimetype='image/png',
        as_attachment=True,
        download_name='captcha.png'
    )

@app.route('/verify-captcha', methods=['POST'])
@limiter.limit("10 per minute")
def verify_captcha():
    """Verify the CAPTCHA response."""
    data = request.get_json()
    session_id = data.get('session_id')
    user_input = data.get('captcha_input')
    
    if not session_id or not user_input:
        return jsonify({'error': 'Session ID and CAPTCHA input required'}), 400
    
    # Get stored CAPTCHA
    stored_captcha = redis_client.get(f'captcha:{session_id}')
    
    if not stored_captcha:
        return jsonify({'error': 'CAPTCHA expired or invalid session'}), 400
    
    # Compare and delete the CAPTCHA after verification
    is_valid = user_input.upper() == stored_captcha.decode('utf-8')
    redis_client.delete(f'captcha:{session_id}')
    
    return jsonify({
        'valid': is_valid,
        'message': 'CAPTCHA verified successfully' if is_valid else 'Invalid CAPTCHA'
    })

if __name__ == '__main__':
    app.run(debug=True) 