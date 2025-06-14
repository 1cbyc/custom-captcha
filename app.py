from flask import Flask, request, jsonify, send_file, session, render_template, redirect, url_for, send_from_directory
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import random
import string
import io
import time
import hashlib
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

# List of User-Agent strings to block (case-insensitive for comparison)
# This list includes common bot names, even those of 'good' bots like Googlebot,
# to meet the requirement of blocking all bot traffic.
BLOCKED_USER_AGENTS = [
    "bot", "crawl", "spider", "scraper", "http client", "http agent",
    "python-requests", "python-urllib", "php", "java", "curl", "wget",
    "googlebot", "bingbot", "slurp", "duckduckbot", "yandexbot",
    "baiduspider", "aolbuild", "yahoo! slurp", "facebookexternalhit",
    "twitterbot", "pinterestbot", "linkedinbot", "slackbot", "discordbot",
    "semrushbot", "ahrefsbot", "mj12bot", "dotbot", "lipperhey",
    "petalbot", "proximic", "screaming frog", "masscan", "nmap",
    "nikto", "sqlmap", "zmscan", "goby", "dirbuster", "wfuzz",
    "arachni", "netsparker", "burpsuite", "zap", "go-http-client",
    "okhttp", "headlesschrome", "phantomjs", "puppeteer", "selenium",
    "mozilla/5.0 (compatible; dotbot/1.1; http://www.dotbot.com/)",
    "mozilla/5.0 (compatible; linkcheck/9.0; +http://www.linkcheck.com/)",
    "mozilla/5.0 (compatible; uptimebot/1.0; +http://www.uptimebot.com/)",
    "mozilla/5.0 (compatible; megaindex.org/bot;)",
    "mozilla/5.0 (compatible; systranbot/1.0; +http://www.systrangroup.com/)",
    "mozilla/5.0 (compatible; spbot/1.0; +http://www.spbot.com/)",
    "applebot", "mediapartners-google", "adsbot-google", "google-safe-browsing",
    "msnbot", "duckduckgo-favicons-bot", "yahoocrawler", "google-structured-data-testing-tool"
]

# List of IP addresses to block
# In a real application, this would ideally be loaded from a database or configuration file
BLOCKED_IPS = [
    # "192.168.1.100", # Example IP to block
    # "10.0.0.5" # Another example
]

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Before every request, check the User-Agent
@app.before_request
def block_bots():
    user_agent = request.headers.get('User-Agent')
    if user_agent:
        user_agent_lower = user_agent.lower()
        for bot_ua in BLOCKED_USER_AGENTS:
            if bot_ua.lower() in user_agent_lower:
                print(f"Blocking request from User-Agent: {user_agent}") # Log blocked attempts
                return "Forbidden: Access denied for automated clients.", 403
    
    # Check for blocked IP addresses
    client_ip = request.remote_addr
    if client_ip in BLOCKED_IPS:
        print(f"Blocking request from IP: {client_ip}") # Log blocked attempts
        return "Forbidden: Access denied for this IP address.", 403

    # Basic Referer check for CAPTCHA-related endpoints
    if request.path in ['/generate-captcha', '/verify-captcha']:
        referer = request.headers.get('Referer')
        if not referer or not referer.startswith(request.url_root):
            print(f"Suspicious request: Missing or invalid Referer for {request.path} from {referer}")
            # You could choose to block here, but for now, we'll just log.
            # return "Forbidden: Invalid Referer.", 403

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
        # Try to use a larger font size
        try:
            font = ImageFont.truetype("arial.ttf", 17)  # Increased font size
        except:
            font = ImageFont.load_default()
        draw.text((x, y), char, fill=color, font=font, angle=angle)
    
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

@app.route('/')
def index():
    """Serve the main page and clear session for new CAPTCHA."""
    session.pop('captcha_verified', None) # Clear CAPTCHA verification status
    return render_template('index.html')

@app.route('/pepu/')
@app.route('/pepu/<path:filename>')
def pepu_site(filename='index.html'):
    """Serve the pepu website after CAPTCHA verification."""
    if session.get('captcha_verified'):
        return send_from_directory('static/pepu', filename)
    return redirect(url_for('index'))

@app.route('/app/')
@app.route('/app/<path:filename>')
def app_site(filename='index.html'):
    """Serve the app content within the pepu website."""
    if session.get('captcha_verified'):
        return send_from_directory('static/pepu/app', filename)
    return redirect(url_for('index'))

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
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/verify-captcha', methods=['POST'])
@limiter.limit("10 per minute")
def verify_captcha():
    """Verify the CAPTCHA response."""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        user_input = data.get('captcha_input')
        honeypot_input = data.get('_honey_pot') # Get honeypot field value
        js_challenge_response = data.get('js_challenge_response') # Get JS challenge response

        # --- Debugging Prints ---
        print(f"DEBUG: Received session_id: {session_id}")
        print(f"DEBUG: Received user_input: {user_input}")
        print(f"DEBUG: Received honeypot_input: {honeypot_input}")
        print(f"DEBUG: Received js_challenge_response: {js_challenge_response}")
        # ------------------------

        # Check honeypot first: if it's filled, it's a bot
        if honeypot_input:
            print(f"Blocking request: Honeypot field was filled.")
            return "Forbidden: Access denied due to honeypot activation.", 403
        
        if not session_id or not user_input or not js_challenge_response:
            print(f"DEBUG: Missing required fields. session_id: {session_id}, user_input: {user_input}, js_challenge_response: {js_challenge_response}")
            return jsonify({'error': 'Session ID, CAPTCHA input, and JS challenge response required'}), 400
        
        # Get stored CAPTCHA
        stored_data = captcha_store.get(session_id)
        
        # --- Debugging Prints ---
        if stored_data:
            print(f"DEBUG: Stored CAPTCHA text: {stored_data.get('text')}")
            print(f"DEBUG: Stored CAPTCHA expires: {stored_data.get('expires')}")
        else:
            print(f"DEBUG: No stored CAPTCHA data found for session_id: {session_id}")
        # ------------------------

        if not stored_data or time.time() > stored_data['expires']:
            print(f"DEBUG: CAPTCHA expired or invalid session check failed. stored_data: {stored_data is not None}, expired: {time.time() > stored_data['expires'] if stored_data else 'N/A'}")
            return jsonify({'error': 'CAPTCHA expired or invalid session'}), 400

        # Verify JS challenge solution (checking for the fixed string)
        if js_challenge_response != 'js_executed_123':
            print(f"Blocking request: JS challenge failed. Expected 'js_executed_123', Received: {js_challenge_response}")
            return jsonify({'error': 'JS Challenge failed'}), 403

        # Increment attempts
        stored_data['attempts'] += 1
        
        # Check if too many attempts
        if stored_data['attempts'] > 3:
            del captcha_store[session_id]
            return jsonify({'error': 'Too many attempts'}), 429
        
        # Compare and delete the CAPTCHA after verification
        is_valid = user_input.upper() == stored_data['text'].upper()

        # --- Debugging Prints ---
        print(f"DEBUG: CAPTCHA text comparison - User Input: {user_input.upper()}, Stored Text: {stored_data['text'].upper()}, Is Valid: {is_valid}")
        # ------------------------

        if is_valid:
            del captcha_store[session_id]
            session['captcha_verified'] = True  # this will set session variable on successful verification
        
        return jsonify({
            'valid': is_valid,
            'message': 'CAPTCHA verified successfully' if is_valid else 'Invalid CAPTCHA'
        })
    except Exception as e:
        print(f"DEBUG: Exception in verify_captcha: {e}")
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