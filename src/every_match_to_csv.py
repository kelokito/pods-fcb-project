import json
import pandas as pd
import os

EVENTS_DIR = "data/barcelona_2014_2015/events"
OUTPUT_DIR = "data/barcelona_2014_2015/csv"
os.makedirs(OUTPUT_DIR, exist_ok=True)

for filename in os.listdir(EVENTS_DIR):
    if not filename.endswith(".json"):
        continue

    match_id = filename.replace(".json", "")
    filepath = os.path.join(EVENTS_DIR, filename)

    with open(filepath, "r", encoding="utf-8") as f:
        events = json.load(f)

    rows = []

    for ev in events:
        case_id = f"{match_id}-{ev.get('possession', 0)}"
        activity = ev["type"]["name"]

        team = ev.get("team", {}).get("name")
        resource = ev.get("player", {}).get("name")

        x, y = None, None
        if isinstance(ev.get("location"), list) and len(ev["location"]) == 2:
            x, y = ev["location"]

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
            "possession": ev.get("possession"),
            "x": x,
            "y": y
        })

    df = pd.DataFrame(rows)
    out_path = os.path.join(OUTPUT_DIR, f"{match_id}.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
