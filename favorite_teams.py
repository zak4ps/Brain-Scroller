import requests
import json
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# --- CONFIGURATION ---
ANGELS_URL = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId=108&hydrate=team,score"
DUCKS_URL = "https://api-web.nhle.com/v1/club-schedule-season/ANA/20252026"
PACIFIC_TZ = ZoneInfo("America/Los_Angeles")

def fetch_angels():
    try:
        print("Fetching Angels (MLB)...")
        response = requests.get(ANGELS_URL)
        data = response.json()
        dates = data.get('dates', [])
        all_games = []
        for d in dates:
            all_games.extend(d.get('games', []))
        return all_games
    except Exception as e:
        print(f"MLB Error: {e}")
        return []

def fetch_ducks():
    try:
        print("Fetching Ducks (NHL)...")
        response = requests.get(DUCKS_URL)
        data = response.json()
        return data.get('games', [])
    except Exception as e:
        print(f"NHL Error: {e}")
        return []

def format_mlb(game):
    status = game['status']['abstractGameState']
    home = game['teams']['home']
    away = game['teams']['away']
    is_final = status == 'Final'
    
    # Timezone Conversion
    utc_dt = datetime.fromisoformat(game['gameDate'].replace('Z', '+00:00'))
    local_dt = utc_dt.astimezone(PACIFIC_TZ)
    
    time_display = local_dt.strftime('%I:%M %p') if not is_final else "Final"
    # Add Date to title if upcoming
    title_display = "Final Result" if is_final else f"Upcoming - {local_dt.strftime('%b %d')}"

    return {
        "post_id": f"fav_mlb_{game['gamePk']}",
        "article_id": "angels_baseball",
        "type": "Sports",
        "category": "MLB",
        "theme": f"{home['team']['name']} vs {away['team']['name']}",
        "pages": [{
            "title": title_display,
            "league_logo": "https://www.mlbstatic.com/team-logos/league-lgo/1.svg",
            "home_name": home['team']['name'],
            "home_logo": f"https://www.mlbstatic.com/team-logos/{home['team']['id']}.svg",
            "away_name": away['team']['name'],
            "away_logo": f"https://www.mlbstatic.com/team-logos/{away['team']['id']}.svg",
            "score_line": f"{home.get('score', 0)} - {away.get('score', 0)}" if is_final else "vs",
            "status_display": time_display,
            "status_code": "FT" if is_final else "SCH"
        }]
    }

def format_nhl(game):
    state = game.get('gameState')
    is_final = state in ['OFF', 'FINAL']
    home = game['homeTeam']
    away = game['awayTeam']
    
    # Timezone Conversion
    utc_dt = datetime.fromisoformat(game['startTimeUTC'].replace('Z', '+00:00'))
    local_dt = utc_dt.astimezone(PACIFIC_TZ)

    time_display = local_dt.strftime('%I:%M %p') if not is_final else "Final"
    title_display = "Final Result" if is_final else f"Upcoming - {local_dt.strftime('%b %d')}"

    return {
        "post_id": f"fav_nhl_{game['id']}",
        "article_id": "ducks_hockey",
        "type": "Sports",
        "category": "NHL",
        "theme": f"{home['commonName']['default']} vs {away['commonName']['default']}",
        "pages": [{
            "title": title_display,
            "league_logo": "https://assets.nhle.com/logos/nhl/svg/NHL_light.svg",
            "home_name": home['commonName']['default'],
            "home_logo": home['logo'],
            "away_name": away['commonName']['default'],
            "away_logo": away['logo'],
            "score_line": f"{home.get('score', 0)} - {away.get('score', 0)}" if is_final else "vs",
            "status_display": time_display,
            "status_code": "FT" if is_final else "SCH"
        }]
    }

def save_json(data, filename):
    os.makedirs("json", exist_ok=True)
    path = os.path.join("json", filename)
    with open(path, "w", encoding="utf-8-sig") as f:
        json.dump(data, f, indent=4)
    print(f"Saved {len(data)} items to {filename}")

def run_pipeline():
    mlb_raw = fetch_angels()
    mlb_posts = [format_mlb(g) for g in mlb_raw]
    
    nhl_raw = fetch_ducks()
    # Logic to find last finished and next upcoming
    now_utc = datetime.now(timezone.utc)
    nhl_finished = [g for g in nhl_raw if g.get('gameState') in ['OFF', 'FINAL']]
    nhl_upcoming = [g for g in nhl_raw if g.get('gameState') == 'FUT']
    
    selected_nhl = []
    if nhl_finished: selected_nhl.append(nhl_finished[-1])
    if nhl_upcoming: selected_nhl.append(nhl_upcoming[0])
    
    nhl_posts = [format_nhl(g) for g in selected_nhl]

    all_favs = mlb_posts + nhl_posts
    finished = [p for p in all_favs if p['pages'][0]['status_code'] == 'FT']
    scheduled = [p for p in all_favs if p['pages'][0]['status_code'] != 'FT']

    save_json(finished, "finished_favorites.json")
    save_json(scheduled, "scheduled_favorites.json")

if __name__ == "__main__":
    run_pipeline()