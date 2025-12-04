import json
import pandas as pd
import os

EVENTS_DIR = "data/barcelona_2014_2015/events"
MATCHES_DIR = "data/barcelona_2014_2015/matches"
OUTPUT_DIR = "data/barcelona_2014_2015/csv"

os.makedirs(OUTPUT_DIR, exist_ok=True)

for filename in os.listdir(EVENTS_DIR):
    if not filename.endswith(".json"):
        continue

    # ------------------------------
    # Extract match_id
    # ------------------------------
    match_id = filename.replace(".json", "")
    events_path = os.path.join(EVENTS_DIR, filename)
    match_path = os.path.join(MATCHES_DIR, f"{match_id}.json")

    # ------------------------------
    # Load event file
    # ------------------------------
    with open(events_path, "r", encoding="utf-8") as f:
        events = json.load(f)

    # ------------------------------
    # Load match metadata
    # ------------------------------
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
            match_won = None  # Should NEVER happen

    except FileNotFoundError:
        print(f"⚠️ No match metadata available for match_id {match_id}. Setting match_won = None.")
        match_won = None

    rows = []

    # ------------------------------
    # Process each event
    # ------------------------------
    for ev in events:

        team = ev.get("team", {}).get("name")

        # Keep only Barcelona events
        if team is None or team.lower() != "barcelona":
            continue

        case_id = f"{match_id}-{ev.get('possession', 0)}"
        activity = ev["type"]["name"]
        resource = ev.get("player", {}).get("name")

        # Location
        x, y = None, None
        if isinstance(ev.get("location"), list) and len(ev["location"]) == 2:
            x, y = ev["location"]

        # Detect if the event is a goal
        finalize_in_goal = False
        if "shot" in ev:
            outcome = ev["shot"].get("outcome", {}).get("name")
            if outcome == "Goal":
                finalize_in_goal = True

        rows.append({
            "match_id": match_id,
            "match_won": match_won,
            "case_id": case_id,
            "finalize_in_goal": finalize_in_goal,
            "activity": activity,
            "timestamp": ev.get("timestamp"),
            "resource": resource,
            "team": team,
            "period": ev.get("period"),
            "minute": ev.get("minute"),
            "second": ev.get("second"),
            "possession": ev.get("possession"),
            "x": x,
            "y": y
        })

    # ------------------------------
    # Save CSV
    # ------------------------------
    df = pd.DataFrame(rows)
    out_path = os.path.join(OUTPUT_DIR, f"{match_id}.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
