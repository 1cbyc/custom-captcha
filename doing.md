# what i have been doing


i added a max-width: 380px; to allow the entire "captcha-container" to be compact.

all done now, i want to make the enter key also trigger the verify button at least.
what it did was that i adde dthis:
```html
<input type="text" id="captcha-input" placeholder="Enter CAPTCHA text" onkeydown="if(event.key === 'Enter') verifyCaptcha()">
```