import json
import requests
import os

BASE_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"

# Output folders
os.makedirs("data/barcelona_2014_2015/matches", exist_ok=True)
os.makedirs("data/barcelona_2014_2015/events", exist_ok=True)

COMPETITION_ID = 11  # La Liga

# Load competitions.json to find season ID for 2014/2015
competitions = requests.get(f"{BASE_URL}/competitions.json").json()

# Find season_id for La Liga 2014/2015
season_id = None
for c in competitions:
    if c["competition_id"] == COMPETITION_ID and c["season_name"] == "2014/2015":
        season_id = c["season_id"]
        break

if season_id is None:
    raise RuntimeError("Could not find season_id for La Liga 2014/2015")

print(f"Using La Liga season_id: {season_id}")

# Download matches file
matches_url = f"{BASE_URL}/matches/{COMPETITION_ID}/{season_id}.json"
matches = requests.get(matches_url).json()

print(f"Total matches in season: {len(matches)}")

# Process Barcelona matches
for match in matches:
    home = match["home_team"]["home_team_name"]
    away = match["away_team"]["away_team_name"]

    if home == "Barcelona" or away == "Barcelona":
        match_id = match["match_id"]
        print(f" - Barcelona match found: {match_id} ({home} vs {away})")

        # Save match JSON
        with open(f"data/barcelona_2014_2015/matches/{match_id}.json", "w") as f:
            json.dump(match, f, indent=2)

        # Download events
        events_url = f"{BASE_URL}/events/{match_id}.json"
        events = requests.get(events_url).json()

        with open(f"data/barcelona_2014_2015/events/{match_id}.json", "w") as f:
            json.dump(events, f, indent=2)

print("Done.")
