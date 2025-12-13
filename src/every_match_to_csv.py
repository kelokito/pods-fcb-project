import json
import pandas as pd
import os
from collections import defaultdict


EVENTS_DIR = "data/barcelona_2014_2015/events"
MATCHES_DIR = "data/barcelona_2014_2015/matches"
OUTPUT_DIR = "data/barcelona_2014_2015/csv"
os.makedirs(OUTPUT_DIR, exist_ok=True)


EXCLUDED_ACTIVITIES = {
    "Half Start", "Half End", "Substitution", "Tactical Shift",
    "Player On", "Player Off", "Injury Stoppage", "Offside",
    "Shield", "Error", "Foul Committed", "Foul Won",
    "Camera On", "Camera Off", "Starting XI", "Bad Behaviour"
}


# -----------------------------------------------------
# 1. Load event JSON file
# -----------------------------------------------------
def load_events(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# -----------------------------------------------------
# 2. Load match metadata (winner, teams, score…)
# -----------------------------------------------------
def load_match_metadata(match_id):
    match_path = os.path.join(MATCHES_DIR, f"{match_id}.json")
    try:
        with open(match_path, "r", encoding="utf-8") as f:
            match = json.load(f)

        home = match["home_team"]["home_team_name"]
        away = match["away_team"]["away_team_name"]
        h_score = match["home_score"]
        a_score = match["away_score"]

        if home.lower() == "barcelona":
            match_won = h_score > a_score
        elif away.lower() == "barcelona":
            match_won = a_score > h_score
        else:
            match_won = None

        return match_won

    except FileNotFoundError:
        print(f"⚠ Missing metadata for match {match_id}")
        return None


# -----------------------------------------------------
# 3. Identify goal-ending possessions
# -----------------------------------------------------
def get_goal_possessions(events):
    return {
        ev.get("possession")
        for ev in events
        if ev.get("team", {}).get("name", "").lower() == "barcelona"
        and "shot" in ev
        and ev["shot"].get("outcome", {}).get("name") == "Goal"
    }


# -----------------------------------------------------
# 4. Count valid actions per possession
# -----------------------------------------------------
def count_actions(events):
    counts = defaultdict(int)
    for ev in events:
        if ev.get("team", {}).get("name", "").lower() != "barcelona":
            continue
        if ev["type"]["name"] in EXCLUDED_ACTIVITIES:
            continue
        counts[ev.get("possession")] += 1
    return counts


# -----------------------------------------------------
# 5. Classify pitch zone
# -----------------------------------------------------
def classify_zone(x, y):
    if x is None or y is None:
        return None  # triggers row removal
    if x < 18:
        return "Own Penalty Area"
    elif x < 40:
        return "Own Half"
    elif x < 60:
        return "Midfield Zone"
    elif x < 80:
        return "Attacking 3/4"
    elif x < 102:
        return "Opponent Half"
    else:
        return "Opponent Penalty Area"


# -----------------------------------------------------
# 5b. Classify vertical zone
# -----------------------------------------------------
def classify_vertical(y):
    if y < 0:
        y = 0
    if y > 80:
        y = 80

    if y < 20:
        return "left"
    elif y < 40:
        return "center-left"
    elif y < 60:
        return "center-right"
    else:
        return "right"


# -----------------------------------------------------
# 6. Classify possession type based on action count
# -----------------------------------------------------
def classify_possession_type(n):
    if n < 5:
        return "Fast Transition"
    elif n < 20:
        return "Normal Play"
    else:
        return "Long Buildup"


# -----------------------------------------------------
# 7. Build rows (DROP rows with missing x,y)
# -----------------------------------------------------
def build_event_rows(events, match_id, goal_possessions, action_counts, match_won):
    rows = []

    for ev in events:

        # keep only Barcelona actions
        if ev.get("team", {}).get("name", "").lower() != "barcelona":
            continue

        activity = ev["type"]["name"]
        if activity in EXCLUDED_ACTIVITIES:
            continue

        possession = ev.get("possession")
        case_id = f"{match_id}-{possession}"

        # ---- Coordinates ----
        loc = ev.get("location")
        if not (isinstance(loc, list) and len(loc) == 2):
            continue  # REMOVE row completely

        x, y = loc
        zone = classify_zone(x, y)
        if zone is None:
            continue  # REMOVE row if zone classification fails

        vertical = classify_vertical(y)

        finalize_in_goal = possession in goal_possessions

        possession_type = classify_possession_type(action_counts[possession])

        # ---- Normal event ----
        rows.append({
            "match_id": match_id,
            "case_id": case_id,
            "activity": activity,
            "timestamp": ev.get("timestamp"),
            "resource": ev.get("player", {}).get("name"),
            "team": "Barcelona",
            "period": ev.get("period"),
            "minute": ev.get("minute"),
            "second": ev.get("second"),
            "possession": possession,
            "zone": zone,
            "vertical": vertical,
            "finalize_in_goal": finalize_in_goal,
            "match_won": match_won,
            "possession_type": possession_type
        })

        # ---- Synthetic goal event ----
        if activity == "Shot" and ev["shot"].get("outcome", {}).get("name") == "Goal":
            rows.append({
                "match_id": match_id,
                "case_id": case_id,
                "activity": "Goal",
                "timestamp": ev.get("timestamp"),
                "resource": ev.get("player", {}).get("name"),
                "team": "Barcelona",
                "period": ev.get("period"),
                "minute": ev.get("minute"),
                "second": ev.get("second"),
                "possession": possession,
                "zone": zone,
                "vertical": vertical,
                "finalize_in_goal": True,
                "match_won": match_won,
                "possession_type": possession_type
            })

    return rows


# =====================================================
# MAIN SCRIPT
# =====================================================
for filename in os.listdir(EVENTS_DIR):

    if not filename.endswith(".json"):
        continue

    match_id = filename.replace(".json", "")

    events = load_events(os.path.join(EVENTS_DIR, filename))
    match_won = load_match_metadata(match_id)

    goal_possessions = get_goal_possessions(events)
    action_counts = count_actions(events)

    rows = build_event_rows(
        events, match_id, goal_possessions, action_counts, match_won
    )

    df = pd.DataFrame(rows)
    out_path = os.path.join(OUTPUT_DIR, f"{match_id}.csv")
    df.to_csv(out_path, index=False)

    print(f"Saved: {out_path}")
