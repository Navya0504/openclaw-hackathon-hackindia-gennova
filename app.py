import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from urllib.parse import urlparse

app = Flask(__name__)

def verify_link_content(url):
    try:
        suspicious_exts = [".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", "bit.ly", "t.co", "shorturl.at"]

        if any(ext in url.lower() for ext in suspicious_exts):
            return "FAKE", "OFFICIAL ALERT", "High-risk or shortened URL detected."

        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, timeout=7, headers=headers, allow_redirects=True)

        orig_dom = urlparse(url).netloc.replace('www.', '')
        final_dom = urlparse(response.url).netloc.replace('www.', '')

        if orig_dom != final_dom:
            return "FAKE", "OFFICIAL ALERT", f"Redirect detected to {final_dom}"

        if not response.url.startswith("https://"):
            return "FAKE", "OFFICIAL ALERT", "Website is not secure (HTTP detected)."

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text().lower()

        scam_words = ["lottery","winner","otp","password","giveaway","free recharge"]

        for word in scam_words:
            if word in text:
                return "FAKE", "OFFICIAL ALERT", f"Suspicious keyword detected: {word}"

        return "REAL", "ANALYSIS COMPLETE", "This website appears safe."

    except Exception:
        return "FAKE", "OFFICIAL ALERT", "Could not access the website."


def analyze_message(text):

    url_match = re.search(r'(https?://\S+)', text)

    if url_match:
        url = url_match.group(0)

        status, message, details = verify_link_content(url)

        return {
            "status": status,
            "message": message,
            "details": details,
            "url": url
        }

    return {
        "status": "FAKE",
        "message": "NO LINK",
        "details": "Please provide a message containing a URL.",
        "url": "#"
    }


@app.route("/", methods=["GET","POST"])
def home():

    report = None

    if request.method == "POST":
        text = request.form["news"]
        report = analyze_message(text)

    return render_template("index.html", report=report)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0",port=5000)