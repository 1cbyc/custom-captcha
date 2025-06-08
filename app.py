from flask import Flask, request, jsonify, send_file, session
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import random
import string
import io
import time
import hashlib
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from datetime import datetime, timedelta
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('captcha.log', maxBytes=10000000, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Initialize rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# In-memory storage for CAPTCHA challenges
captcha_store = {}

def generate_captcha_text():
    """Generate a random CAPTCHA text with mixed case and numbers."""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=6))

def create_captcha_image(text):
    """Create a CAPTCHA image with advanced anti-bot measures."""
    # Create a new image with a white background
    width = 200
    height = 80
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Add random background noise
    for _ in range(1000):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.point((x, y), fill='gray')
    
    # Add random lines
    for _ in range(8):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill='gray', width=2)
    
    # Add text with random positioning, rotation, and color
    for i, char in enumerate(text):
        x = 20 + i * 30
        y = random.randint(10, 40)
        angle = random.randint(-30, 30)
        color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
        draw.text((x, y), char, fill=color, font=None, angle=angle)
    
    # Apply some filters to make it harder for OCR
    image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
    image = image.filter(ImageFilter.EDGE_ENHANCE)
    
    # Add some random distortion
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(random.uniform(1.0, 1.5))
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

def generate_session_id():
    """Generate a unique session ID."""
    return hashlib.sha256(str(time.time()).encode()).hexdigest()

@app.route('/generate-captcha', methods=['GET'])
@limiter.limit("10 per minute")
def generate_captcha():
    """Generate a new CAPTCHA challenge."""
    try:
        captcha_text = generate_captcha_text()
        session_id = request.args.get('session_id', generate_session_id())
        
        # Store CAPTCHA with expiration
        captcha_store[session_id] = {
            'text': captcha_text,
            'expires': time.time() + 300,  # 5 minutes
            'attempts': 0
        }
        
        # Generate and return the image
        image = create_captcha_image(captcha_text)
        return send_file(
            image,
            mimetype='image/png',
            as_attachment=True,
            download_name='captcha.png'
        )
    except Exception as e:
        logger.error(f"Error generating CAPTCHA: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/verify-captcha', methods=['POST'])
@limiter.limit("10 per minute")
def verify_captcha():
    """Verify the CAPTCHA response."""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        user_input = data.get('captcha_input')
        
        if not session_id or not user_input:
            return jsonify({'error': 'Session ID and CAPTCHA input required'}), 400
        
        # Get stored CAPTCHA
        stored_data = captcha_store.get(session_id)
        
        if not stored_data or time.time() > stored_data['expires']:
            return jsonify({'error': 'CAPTCHA expired or invalid session'}), 400
        
        # Increment attempts
        stored_data['attempts'] += 1
        
        # Check if too many attempts
        if stored_data['attempts'] > 3:
            del captcha_store[session_id]
            return jsonify({'error': 'Too many attempts'}), 429
        
        # Compare and delete the CAPTCHA after verification
        is_valid = user_input.upper() == stored_data['text'].upper()
        if is_valid:
            del captcha_store[session_id]
        
        return jsonify({
            'valid': is_valid,
            'message': 'CAPTCHA verified successfully' if is_valid else 'Invalid CAPTCHA'
        })
    except Exception as e:
        logger.error(f"Error verifying CAPTCHA: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded errors."""
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': str(e.description)
    }), 429

if __name__ == '__main__':
    app.run(debug=True) 