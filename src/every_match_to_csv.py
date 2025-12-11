import json
import pandas as pd
import os

EVENTS_DIR = "data/barcelona_2014_2015/events"
MATCHES_DIR = "data/barcelona_2014_2015/matches"
OUTPUT_DIR = "data/barcelona_2014_2015/csv"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------------------------------
# Activities to REMOVE (ignored completely)
# -----------------------------------------------------
EXCLUDED_ACTIVITIES = [
    "Half Start", "Half End", "Substitution", "Tactical Shift",
    "Player On", "Player Off", "Injury Stoppage", "Offside",
    "Shield", "Error", "Foul Committed", "Foul Won",
    "Camera On", "Camera Off", "Starting XI", "Bad Behaviour"
]

# -----------------------------------------------------
# Zone classification function (6 zones max)
# -----------------------------------------------------
def classify_zone(x, y):
    if x is None:
        return "Unknown"

    # 120m × 80m pitch → StatsBomb standard

    if x < 18:
        return "Own Penalty Area"               # Zone 1
    elif x < 40:
        return "Own Half"                       # Zone 2
    elif x < 60:
        return "Midfield Zone"                  # Zone 3
    elif x < 80:
        return "Attacking 3/4"                  # Zone 4
    elif x < 102:
        return "Opponent Half"                  # Zone 5
    else:
        return "Opponent Penalty Area"          # Zone 6


for filename in os.listdir(EVENTS_DIR):
    if not filename.endswith(".json"):
        continue

    match_id = filename.replace(".json", "")
    events_path = os.path.join(EVENTS_DIR, filename)
    match_path = os.path.join(MATCHES_DIR, f"{match_id}.json")

    with open(events_path, "r", encoding="utf-8") as f:
        events = json.load(f)

    # ---- Load match metadata ----
    try:
        with open(match_path, "r", encoding="utf-8") as f:
            match = json.load(f)

        home_team = match["home_team"]["home_team_name"]
        away_team = match["away_team"]["away_team_name"]
        home_score = match["home_score"]
        away_score = match["away_score"]

        if home_team.lower() == "barcelona":
            match_won = home_score > away_score
        elif away_team.lower() == "barcelona":
            match_won = away_score > home_score
        else:
            match_won = None

    except FileNotFoundError:
        print(f"⚠ No match metadata for {match_id}, match_won set to None.")
        match_won = None

    # -----------------------------------------------------
    # Identify ALL possessions containing goals
    # -----------------------------------------------------
    goal_possessions = set()

    for ev in events:
        if ev.get("team", {}).get("name", "").lower() != "barcelona":
            continue

        if "shot" in ev and ev["shot"].get("outcome", {}).get("name") == "Goal":
            goal_possessions.add(ev.get("possession"))

    # -----------------------------------------------------
    # Process events
    # -----------------------------------------------------
    rows = []

    for ev in events:

        team = ev.get("team", {}).get("name")
        if team is None or team.lower() != "barcelona":
            continue

        activity = ev["type"]["name"]

        # Skip excluded activities
        if activity in EXCLUDED_ACTIVITIES:
            continue

        possession = ev.get("possession")
        case_id = f"{match_id}-{possession}"

        resource = ev.get("player", {}).get("name")

        # Coordinates
        x, y = None, None
        loc = ev.get("location")
        if isinstance(loc, list) and len(loc) == 2:
            x, y = loc

        # Zone
        zone = classify_zone(x, y)

        # Flag goal possessions
        finalize_in_goal = possession in goal_possessions

        # Normal event
        rows.append({
            "match_id": match_id,
            "case_id": case_id,
            "activity": activity,
            "timestamp": ev.get("timestamp"),
            "resource": resource,
            "team": team,
            "period": ev.get("period"),
            "minute": ev.get("minute"),
            "second": ev.get("second"),
            "possession": possession,
            "zone": zone,
            "finalize_in_goal": finalize_in_goal,
            "match_won": match_won
        })

        # Add synthetic Goal event
        if activity == "Shot" and ev["shot"].get("outcome", {}).get("name") == "Goal":
            rows.append({
                "match_id": match_id,
                "case_id": case_id,
                "activity": "Goal",
                "timestamp": ev.get("timestamp"),
                "resource": resource,
                "team": team,
                "period": ev.get("period"),
                "minute": ev.get("minute"),
                "second": ev.get("second"),
                "possession": possession,
                "zone": zone,
                "finalize_in_goal": True,
                "match_won": match_won
            })

    # Save CSV
    df = pd.DataFrame(rows)
    out_path = os.path.join(OUTPUT_DIR, f"{match_id}.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
