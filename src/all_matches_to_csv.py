import json
import pandas as pd
import os

EVENTS_DIR = "data/barcelona_2014_2015/events"
OUTPUT_CSV = "data/barcelona_2014_2015_eventlog.csv"

rows = []

for filename in os.listdir(EVENTS_DIR):
    if not filename.endswith(".json"):
        continue

    match_id = filename.replace(".json", "")
    filepath = os.path.join(EVENTS_DIR, filename)

    with open(filepath, "r", encoding="utf-8") as f:
        events = json.load(f)

    for ev in events:
        case_id = f"{match_id}-{ev.get('possession', 0)}"
        activity = ev["type"]["name"]
        timestamp = ev.get("timestamp")

        team = ev.get("team", {}).get("name")
        resource = ev.get("player", {}).get("name")

        # some events have no coordinates
        x, y = None, None
        if isinstance(ev.get("location"), list) and len(ev["location"]) == 2:
            x, y = ev["location"]

        rows.append({
            "match_id": match_id,
            "case_id": case_id,
            "activity": activity,
            "timestamp": timestamp,
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
df.to_csv(OUTPUT_CSV, index=False)

print(f"CSV created: {OUTPUT_CSV}")
