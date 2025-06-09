# Custom CAPTCHA System

A robust CAPTCHA system designed to protect your websites from automated crawling and bot access. This implementation provides a solution that can be integrated into any website to prevent unwanted bot traffic.

## Features

- Advanced image-based CAPTCHA generation
- Rate limiting to prevent brute force attempts
- Session-based validation
- Anti-bot measures including:
  - Random text positioning and rotation
  - Background noise and patterns
  - Image distortion and filters
  - Mixed case and number combinations
- Simple integration with any website
- Attempt limiting (3 attempts per CAPTCHA)
- 5-minute expiration for CAPTCHA challenges

## Installation

1. Clone this repository:
```bash
git clone https://github.com/1cbyc/custom-captcha.git
cd custom-captcha
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# On Windows
.\venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

4. Install the required dependencies:
```bash
pip install -r requirements.txt
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

2. CAPTCHA Security
   - Random text generation
   - Image distortion and noise
   - Character rotation
   - Background patterns
   - Mixed case and numbers
   - 3 attempts per CAPTCHA
   - 5-minute expiration

3. Session Management
   - Unique session IDs
   - One-time use tokens
   - Automatic expiration

## Customization

You can customize the CAPTCHA by modifying the following in `app.py`:

- Text length and character set in `generate_captcha_text()`
- Image size and appearance in `create_captcha_image()`
- Rate limiting rules in the `@limiter.limit()` decorators
- Attempt limits and expiration time in the verification logic

## Side Note

- If you want to embed your websites, or web projects to be protected with this system, you can add the folder to the static folder and replace the `pepu` folder with your own project folder, and then go to the `app.py` python script to add the route with your web project and also add all sub folders that are pages too as a route to make sure it runs properly.

## Contributing

Feel free to submit issues and enhancement requests! 