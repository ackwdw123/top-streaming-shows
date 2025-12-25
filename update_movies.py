import os
import requests
from datetime import datetime
import json

TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
REGION = "US"

# Provider → LG App ID mapping
LG_APP_MAP = {
    "Netflix": "com.webos.app.netflix",
    "Hulu": "com.webos.app.hulu",
    "Disney Plus": "com.webos.app.disneyplus",
    "Disney+": "com.webos.app.disneyplus",
    "Amazon Prime Video": "com.webos.app.primevideo",

    # Apple family
    "Apple TV Plus": "com.webos.app.appletv",
    "Apple TV+": "com.webos.app.appletv",
    "Apple TV": "com.webos.app.appletv",
    "Apple TV App": "com.webos.app.appletv",
    "Apple TV Amazon Channel": "com.webos.app.appletv",
    "Apple iTunes": "com.webos.app.appletv",

    # Max family
    "Max": "com.webos.app.hbomax",
    "HBO Max": "com.webos.app.hbomax",

    # AMC family (no dedicated LG app)
    "AMC": None,
    "AMC+": None,
    "AMC Plus": None,
    "AMC Premiere": None,

    # Starz family
    "Starz": "com.starz.starzplay",
    "Starz Play": "com.starz.starzplay",
    "Starz Amazon Channel": "com.starz.starzplay",
    "Starz Apple TV Channel": "com.starz.starzplay",

    # Spectrum family
    "Spectrum": "com.lge.app.spectrum",
    "Spectrum TV": "com.lge.app.spectrum",
    "Spectrum On Demand": "com.lge.app.spectrum",
}

# Provider → Icon filename mapping
PROVIDER_ICONS = {
    "Netflix": "netflix.png",
    "Hulu": "hulu.png",
    "Disney Plus": "disneyplus.png",
    "Disney+": "disneyplus.png",
    "Amazon Prime Video": "primevideo.png",

    # Apple family
    "Apple TV Plus": "appletv.png",
    "Apple TV+": "appletv.png",
    "Apple TV": "appletv.png",
    "Apple TV App": "appletv.png",
    "Apple TV Amazon Channel": "appletv.png",
    "Apple iTunes": "appletv.png",

    # Max family
    "Max": "max.png",
    "HBO Max": "max.png",

    # AMC family
    "AMC": "amc.png",
    "AMC+": "amc.png",
    "AMC Plus": "amc.png",
    "AMC Premiere": "amc.png",

    # Starz family
    "Starz": "starz.png",
    "Starz Play": "starz.png",
    "Starz Amazon Channel": "starz.png",
    "Starz Apple TV Channel": "starz.png",

    # Spectrum family
    "Spectrum": "spectrum.png",
    "Spectrum TV": "spectrum.png",
    "Spectrum On Demand": "spectrum.png",
}

def tmdb_get(path, params=None):
    if params is None:
        params = {}
    params["api_key"] = TMDB_API_KEY
    response = requests.get(f"{TMDB_BASE_URL}{path}", params=params)
    response.raise_for_status()
    return response.json()

def fetch_movie_providers(movie_id):
    data = tmdb_get(f"/movie/{movie_id}/watch/providers")
    results = data.get("results", {})
    us = results.get(REGION, {})

    flatrate = us.get("flatrate", []) or []
    buy = us.get("buy", []) or []
    rent = us.get("rent", []) or []

    providers = []

    for item in flatrate:
        providers.append(item.get("provider_name"))
    if not providers:
        for item in buy:
            providers.append(item.get("provider_name"))
    if not providers:
        for item in rent:
            providers.append(item.get("provider_name"))

    seen = set()
    unique = []
    for p in providers:
        if p and p not in seen:
            seen.add(p)
            unique.append(p)
    return unique

def fetch_trending_movies_us_only(limit=10):
    data = tmdb_get("/trending/movie/day")
    results = data.get("results", [])

    us_movies = []
    for item in results:
        movie_id = item.get("id")
        providers = fetch_movie_providers(movie_id)

        # Only include movies with at least one US provider
        if providers:
            us_movies.append(item)

        if len(us_movies) == limit:
            break

    return us_movies

def build_movie_record(item):
    movie_id = item.get("id")
    title = item.get("title") or item.get("original_title") or "Unknown Title"
    overview = item.get("overview") or ""
    vote = item.get("vote_average") or 0
    release_date = item.get("release_date") or ""
    poster_path = item.get("poster_path")
    poster_url = f"{IMAGE_BASE}{poster_path}" if poster_path else None
    tmdb_url = f"https://www.themoviedb.org/movie/{movie_id}" if movie_id else None

    providers = fetch_movie_providers(movie_id) if movie_id else []

    launch_app_id = None
    if providers:
        first_provider = providers[0]
        launch_app_id = LG_APP_MAP.get(first_provider)

    return {
        "id": movie_id,
        "title": title,
        "overview": overview,
        "rating": round(vote, 1) if vote else None,
        "release_date": release_date,
        "poster_url": poster_url,
        "tmdb_url": tmdb_url,
        "providers": providers,
        "launch_app_id": launch_app_id,
    }

def generate_movies_json(movies):
    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "source": "TMDB",
        "region": REGION,
        "type": "movie",
        "movies": movies,
    }
    with open("movies.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

def generate_movies_html(movies):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    rows = ""
    for idx, movie in enumerate(movies, start=1):
        providers = movie["providers"]

        provider_icons_html = ""
        for p in providers:
            icon = PROVIDER_ICONS.get(p)
            if icon:
                provider_icons_html += (
                    f"<img src='icons/{icon}' class='provider-icon' alt='{p}' />"
                )

        poster = (
            f"<img src='{movie['poster_url']}' "
            f"alt='Poster for {movie['title']}' "
            f"style='height:140px;border-radius:6px;'/>"
            if movie["poster_url"]
            else ""
        )
        rating = movie["rating"] if movie["rating"] is not None else "—"

        if movie["launch_app_id"]:
            launch_button = f"""
            <a href="lgtv://{movie['launch_app_id']}"
               style="
                 display:inline-block;
                 padding:8px 14px;
                 background:#4ea3ff;
                 color:#000;
                 border-radius:6px;
                 text-decoration:none;
                 font-weight:600;
               ">
               Launch App
            </a>
            """
        else:
            launch_button = ""

        rows += f"""
        <tr>
          <td style="text-align:center; color:#999;">{idx}</td>

          <td style="display:flex; gap:16px; align-items:center;">
            {poster}
            <div>
              <div style="font-size:20px; font-weight:600;">{movie['title']}</div>

              <div style="font-size:14px; color:#aaa; margin-top:4px;">
                Release date: {movie['release_date'] or 'Unknown'}
              </div>

              <div style="font-size:15px; color:#bbb; margin-top:6px; max-width:600px; line-height:1.35;">
                {movie['overview'][:260] + ('…' if len(movie['overview']) > 260 else '')}
              </div>

              <div style="font-size:14px; color:#8fd3ff; margin-top:6px;">
                {provider_icons_html}
              </div>
            </div>
          </td>

          <td style="text-align:center; font-size:18px;">{rating}</td>

          <td class="launch-col" style="text-align:center; vertical-align:middle;">
            {launch_button}
          </td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Top Streaming Movies (TMDB)</title>

  <style>
    body {{
      margin: 0;
      padding: 24px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #05070a;
      color: #f5f5f5;
    }}
    h1 {{
      font-size: 32px;
      margin-bottom: 4px;
    }}
    .subtitle {{
      color: #aaa;
      font-size: 14px;
      margin-bottom: 20px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
    }}
    th, td {{
      padding: 12px 10px;
      border-bottom: 1px solid #222;
      vertical-align: top;
    }}
    th {{
      text-align: left;
      font-size: 14px;
      color: #ccc;
    }}
    .provider-icon {{
      height: 34px;
      margin-right: 10px;
      vertical-align: middle;
    }}
  </style>

  <!-- Robust LG TV detection -->
  <script>
    document.addEventListener("DOMContentLoaded", function () {{
      const ua = navigator.userAgent.toLowerCase();
      const isLGTV =
        ua.includes("web0s") ||
        ua.includes("webos") ||
        ua.includes("lg browser") ||
        ua.includes("lgtv");

      if (isLGTV) {{
        const launchHeader = document.querySelector("th.launch-col");
        if (launchHeader) launchHeader.style.display = "none";

        document.querySelectorAll("td.launch-col").forEach(td => {{
          td.style.display = "none";
        }});
      }}
    }});
  </script>

</head>
<body>
  <h1>Top Streaming Movies</h1>
  <div class="subtitle">
    Auto‑updated from TMDB • Region: {REGION} • Last updated: {now}
  </div>

  <table>
    <thead>
      <tr>
        <th style="width:40px; text-align:center;">#</th>
        <th>Movie</th>
        <th style="width:80px; text-align:center;">Rating</th>
        <th class="launch-col" style="width:120px; text-align:center;">Launch</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>

</body>
</html>
"""
    with open("movies.html", "w", encoding="utf-8") as f:
        f.write(html)

def main():
    if not TMDB_API_KEY:
        raise RuntimeError("TMDB_API_KEY environment variable is not set")

    trending = fetch_trending_movies_us_only(limit=10)
    movies = [build_movie_record(item) for item in trending]

    generate_movies_json(movies)
    generate_movies_html(movies)
    print("movies.html and movies.json updated successfully.")

if __name__ == "__main__":
    main()
