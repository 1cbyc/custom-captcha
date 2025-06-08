# Custom CAPTCHA System

A custom CAPTCHA system designed to protect your websites from automated crawling and bot access. This implementation provides a robust solution that can be integrated into any website.

## Features

- Image-based CAPTCHA generation
- Rate limiting to prevent brute force attempts
- Session-based validation
- Redis-backed storage for scalability
- Simple integration with any website
- Customizable appearance and difficulty

## Prerequisites

- Python 3.8 or higher
- Redis server
- pip (Python package manager)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd custom-captcha
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Make sure Redis server is running on your system:
```bash
# On Windows, start Redis server
redis-server

# On Linux/Mac
sudo service redis-server start
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. The server will start on `http://localhost:5000`

3. To integrate the CAPTCHA into your website:

```html
<!-- Add this where you want the CAPTCHA to appear -->
<div id="captcha-container">
    <img id="captcha-img" src="/generate-captcha?session_id=YOUR_SESSION_ID" alt="CAPTCHA">
    <input type="text" id="captcha-input" placeholder="Enter CAPTCHA text">
    <button onclick="verifyCaptcha()">Verify</button>
</div>

<script>
// Add this JavaScript to your page
async function verifyCaptcha() {
    const input = document.getElementById('captcha-input').value;
    const response = await fetch('/verify-captcha', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: 'YOUR_SESSION_ID',
            captcha_input: input
        })
    });
    const result = await response.json();
    // Handle the verification result
}
</script>
```

## API Endpoints

### Generate CAPTCHA
- **URL**: `/generate-captcha`
- **Method**: `GET`
- **Parameters**: 
  - `session_id` (required): Unique identifier for the session
- **Response**: CAPTCHA image

### Verify CAPTCHA
- **URL**: `/verify-captcha`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "session_id": "your-session-id",
    "captcha_input": "user-input"
  }
  ```
- **Response**:
  ```json
  {
    "valid": true/false,
    "message": "Verification message"
  }
  ```

## Security Features

1. Rate Limiting
   - 10 requests per minute per IP
   - 200 requests per day per IP
   - 50 requests per hour per IP

2. Session Management
   - CAPTCHA tokens expire after 5 minutes
   - One-time use tokens
   - Redis-backed storage for scalability

3. Image Generation
   - Random text generation
   - Noise and distortion
   - Character rotation
   - Background patterns

## Customization

You can customize the CAPTCHA by modifying the following in `app.py`:

- Text length and character set in `generate_captcha_text()`
- Image size and appearance in `create_captcha_image()`
- Rate limiting rules in the `@limiter.limit()` decorators
- Token expiration time in the Redis `setex()` call

## Contributing

Feel free to submit issues and enhancement requests! 