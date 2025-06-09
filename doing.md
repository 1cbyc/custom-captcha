# what i have been doing


i added a max-width: 380px; to allow the entire "captcha-container" to be compact.

all done now, i want to make the enter key also trigger the verify button at least.
what it did was that i adde dthis:
```html
<input type="text" id="captcha-input" placeholder="Enter CAPTCHA text" onkeydown="if(event.key === 'Enter') verifyCaptcha()">
```

okay, i want to make sure when i use the recaptcha it loads a specifc page. cause at the moment, what i want to do is visit a url like "nsisong.com" and you meet the captcha, and when it is done with captcha, it redirects to a specific page. i wanted to just try with a `/success`

okay, works. so now i want to put my full website in there, it is pepu website, so it wil be a pepu folder, let me structure it. i moved the full website folder i have to "static". so i have my website i want to protect with this custom captcha on `static/pepu`. first, i will protect the `pepu` route to only load after `captcha_verified` is marked true.

anyways, i have configured a new route for /app in the pepu folder so it can run well. 

## i named this project custom captcha cause of github. 

the thing is, i want to build a solid way to block all kinds of bot from crawling through websites to raise flags.

1. robotx.txt files is one way to do this
2. next, metatags with noindex and nofollow is another 
3. setting up user agents blocking systems is another thing
4. ip blocking is another thing, but how many ip would you find to block?
5. honeypots is another, i will create hidden form fields that are invisible to human users but bots can see it, so i can block the request
6. rate limiting is recommended too, i already used flask-limiter for this captcha project.
7. this captcha stuff blocks simple bots, but then, some bots are smart.
8. setting up WAFs is another one i do to sieve malicious traffics, but not all my clients or anyone can afford them, so i am not doing that here.
9. i also run javascript challenges that would require simple bots to complete and execute js so it flags it asap.
10. i use referrer checks too


# i collated a bot list

```
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
```


# i also wrote a small honeypot script to trap bots to auto fill a form field in the index.html file:

```html
        <input type="text" id="_honey_pot" name="_honey_pot" style="display: none;" tabindex="-1" autocomplete="off">
```

then, i wrote it in the `app.py` file to detect if the bot fills the request. atleast the defense layer will block automated submissions.
this is the code added right below the captch input side:
```py
        honeypot_input = data.get('_honey_pot') # to get honeypot field value

        # to check honeypot first: if it's filled, it's a bot
        if honeypot_input:
            print(f"Blocking request: Honeypot field {_honey_pot} was filled.")
            return "Forbidden: Access denied due to honeypot activation.", 403
```