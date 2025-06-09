# what i have been doing


i added a max-width: 380px; to allow the entire "captcha-container" to be compact.

all done now, i want to make the enter key also trigger the verify button at least.
what it did was that i adde dthis:
```html
<input type="text" id="captcha-input" placeholder="Enter CAPTCHA text" onkeydown="if(event.key === 'Enter') verifyCaptcha()">
```

okay, i want to make sure when i use the recaptcha it loads a specifc page. cause at the moment, what i want to do is visit a url like "nsisong.com" and you meet the captcha, and when it is done with captcha, it redirects to a specific page. i wanted to just try with a `/success`

okay, works. so now i want to put my full website in there, it is pepu website, so it wil be a pepu folder, let me structure it. i moved the full website folder i have to "static". so i have my website i want to protect with this custom captcha on `static/pepu`. first, i will protect the `pepu` route to only load after `captcha_verified` is marked true.