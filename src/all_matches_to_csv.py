import pandas as pd
import os

EVENTS_DIR = "data/barcelona_2014_2015/csv"
OUTPUT_CSV = "data/barcelona_2014_2015_eventlog.csv"

rows = []

for filename in os.listdir(EVENTS_DIR):
    if not filename.endswith(".csv"):
        continue

    filepath = os.path.join(EVENTS_DIR, filename)
    print(f"Loading: {filepath}")

    df = pd.read_csv(filepath)
    rows.append(df)

# Concatenate all
full_df = pd.concat(rows, ignore_index=True)

# Save output
full_df.to_csv(OUTPUT_CSV, index=False)

print(f"\n✔ Event log saved to: {OUTPUT_CSV}")
print(f"✔ Total rows: {len(full_df)}")
