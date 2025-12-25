import requests
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.rottentomatoes.com/browse/tv_series_browse/sort:popular"

def fetch_top_shows():
    response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    shows = []
    cards = soup.select("a.js-tile-link")[:10]  # Top 10

    for card in cards:
        title = card.get("title", "Unknown Title")
        link = "https://www.rottentomatoes.com" + card.get("href", "")
        shows.append((title, link))

    return shows

def generate_html(shows):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rows = ""
    for title, link in shows:
        rows += f"<tr><td>{title}</td><td><a href='{link}'>Details</a></td></tr>"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Top Streaming Shows</title>
        <style>
            body {{ font-family: Arial; padding: 20px; background: #111; color: #eee; }}
            table {{ width: 100%; border-collapse: collapse; }}
            td {{ padding: 10px; border-bottom: 1px solid #444; }}
            a {{ color: #4ea3ff; }}
        </style>
    </head>
    <body>
        <h1>Top Streaming Shows (Auto‑Updated)</h1>
        <p>Last updated: {now}</p>
        <table>
            {rows}
        </table>
    </body>
    </html>
    """
    return html

def save_html(content):
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    shows = fetch_top_shows()
    html = generate_html(shows)
    save_html(html)
    print("Page updated successfully.")