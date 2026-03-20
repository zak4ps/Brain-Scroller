import requests
import json
import os
from datetime import datetime

# --- CONFIGURATION ---
API_KEY = "48941025dd178f7edcbc9ba6cd6b2e64"
NCAA_ENDPOINT = "https://v1.basketball.api-sports.io/games"

# Status Categories
FINAL_STATUSES = ['FT', 'AOT', 'POST'] 
LIVE_STATUSES = ['Q1', 'Q2', 'Q3', 'Q4', 'OT']

def fetch_ncaa_by_date(target_date):
    """Fetches games from API-Sports for a specific date and filters for NCAA (ID 116)"""
    headers = {'x-apisports-key': API_KEY}
    params = {'date': target_date, 'timezone': 'America/Los_Angeles'} 
    try:
        print(f"Fetching NCAA games for {target_date}...")
        response = requests.get(NCAA_ENDPOINT, headers=headers, params=params)
        data = response.json()
        all_games = data.get('response', [])
        # Filter for NCAA Division I (League 116)
        return [g for g in all_games if g.get('league', {}).get('id') == 116]
    except Exception as e:
        print(f"Error fetching NCAA {target_date}: {e}")
        return []

def format_ncaa_as_post(game_data):
    home = game_data['teams']['home']
    away = game_data['teams']['away']
    status_short = game_data['status']['short']
    
    # EXPLICIT MAPPING: Ensure home stays with home
    h_score = game_data.get('scores', {}).get('home', {}).get('total', 0)
    a_score = game_data.get('scores', {}).get('away', {}).get('total', 0)

    if status_short in FINAL_STATUSES:
        # Match the order of your HTML (Away vs Home or Home vs Away)
        # If your HTML shows Away on Left and Home on Right:
        score_disp = f"{a_score} - {h_score}" 
        time_disp, title = "Final", "Final Result"
    elif status_short in LIVE_STATUSES:
        score_disp = f"{a_score} - {h_score}"
        time_disp, title = game_data.get('time', 'Live'), "Live Now"
    else:
        # For upcoming games, format the time from the 'date' field
        try:
            dt = datetime.fromisoformat(game_data['date'].replace('Z', '+00:00'))
            # Note: API provides local time based on 'timezone' param in fetch
            time_disp = dt.strftime('%I:%M %p')
            title = f"Upcoming - {dt.strftime('%b %d')}"
        except:
            time_disp = game_data.get('time', 'TBD')
            title = "Upcoming"
        score_disp = "vs"

    return {
        "post_id": f"sp_ncaa_{game_data['id']}",
        "article_id": "march_madness_2026",
        "type": "Sports",
        "category": "NCAA",
        "theme": f"{away['name']} vs {home['name']}",
        "pages": [{
            "title": title,
            "league_logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/28/March_Madness_logo.svg/1280px-March_Madness_logo.svg.png", # Clean fallback logo
            "home_name": home['name'], 
            "home_logo": home.get('logo'),
            "away_name": away['name'], 
            "away_logo": away.get('logo'),
            "score_line": score_disp, 
            "status_display": time_disp, 
            "status_code": status_short 
        }]
    }

def save_to_json(posts, filename):
    """Saves posts to the specified JSON file in the /json directory"""
    os.makedirs("json", exist_ok=True)
    file_path = os.path.join("json", filename)
    with open(file_path, "w", encoding="utf-8-sig") as f:
        json.dump(posts, f, indent=4)
    print(f"   -> Saved {len(posts)} posts to {filename}")

def run_pipeline():
    # Hardcoded dates for the 2026 tournament cycle
    today_str = '2026-03-19'
    yesterday_str = '2026-03-18'
    
    # Fetch and combine
    raw_games = fetch_ncaa_by_date(today_str) + fetch_ncaa_by_date(yesterday_str)
    
    # Format
    all_ncaa_posts = [format_ncaa_as_post(g) for g in raw_games]
    
    # Split into finished and upcoming
    finished = [p for p in all_ncaa_posts if p["pages"][0]["status_code"] in FINAL_STATUSES]
    scheduled = [p for p in all_ncaa_posts if p["pages"][0]["status_code"] not in FINAL_STATUSES]

    # Save
    save_to_json(finished, "finished_ncaa.json")
    save_to_json(scheduled, "scheduled_ncaa.json")

if __name__ == "__main__":
    run_pipeline()