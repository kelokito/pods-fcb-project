# 📘 pods-fcb-project

This project extracts, organizes, and converts **FC Barcelona match data** from the open StatsBomb dataset into structured CSV files suitable for analysis and process mining.

The workflow consists of **three Python scripts** located in the `src/` folder:

1. **`get_all_matches_barcelona.py`**
   Downloads all Barcelona matches and their event files for a specific competition and season (La Liga 2014-2015).

2. **`every_match_to_csv.py`**
   Converts each downloaded match’s **event JSON file → CSV**, generating one CSV per match.

3. **`all_matches_to_csv.py`**
   Merges all per-match CSV files into a **single CSV** containing all Barcelona events for the season.

Because event JSON files are large, the raw match data is **not included in the repository**.
After running the scripts, all downloaded and processed data will be stored inside `data/`.

---

## 📂 Project Structure

```
pods-fcb-project/
│
├── src/
├── data/
│       ├── barcelona_2014_2015/        # downloaded match JSON files
│           ├── events/         # downloaded event JSON files
│           ├── matches/        # downloaded match JSON files 
|           ├── csvs/           # downloaded event CSV files per match
|       └── barcelona_2014_2015.csv     # downloaded event CSV files merged
|  
|   ├── get_all_matches_barcelona.py
│   ├── every_match_to_csv.py
│   └── all_matches_to_csv.py
|   
│
└── README.md
```

---

## 🚀 How to Use

### **1. Download all Barcelona matches (La Liga 2014-2015)**

```bash
cd ./src
python get_all_matches_barcelona.py
```

This script:

* Retrieves match metadata
* Detects the Barcelona matches
* Saves each match JSON into `data/matches/`
* Downloads each event file into `data/events/`

---

### **2. Convert each match’s events into CSV**

```bash
python every_match_to_csv.py
```

This script:

* Reads each event JSON from `data/events/`
* Extracts event metadata (activity, timestamp, player, location, etc.)
* Builds process-mining-oriented rows (`case_id`, `possession`, etc.)
* Saves each CSV into `data/per_match_csv/`

---

### **3. Create one unified CSV for all matches**

```bash
python all_matches_to_csv.py
```

This script merges all per-match CSV files into:

```
data/all_events.csv
```

This file includes all Barcelona events for the 2014-2015 season, ideal for:

* Process mining (ProM, PM4Py)
* Event sequence modeling
* Tactical analysis
* Possession chain extraction
* Spatial analytics

---

## 📊 Output Fields

Each event row contains:

| Column     | Description                          |
| ---------- | ------------------------------------ |
| match_id   | StatsBomb match ID                   |
| case_id    | Composite ID: `match_id-possession`  |
| activity   | Event type (Pass, Shot, Carry, etc.) |
| timestamp  | Match timestamp                      |
| team       | Team performing the action           |
| resource   | Player performing the action         |
| possession | Possession sequence number           |
| minute     | Minute of the event                  |
| second     | Second within the minute             |
| period     | First or second half (or extra time) |
| x, y       | Event field coordinates              |

---

## 📦 Dependencies

Install required libraries:

```bash
pip install pandas requests
```

(Optional)
Install PM4Py for process mining:

```bash
pip install pm4py
```

---

## 🙌 Credits

All football event data used in this project comes from the **StatsBomb Open Data initiative**:

**StatsBomb Open Data Repository**
[https://github.com/statsbomb/open-data](https://github.com/statsbomb/open-data)

Data © **StatsBomb Services Limited** – released under the Creative Commons Attribution 4.0 International License (CC BY 4.0).

---

## 📧 Contact / Contributing

Feel free to open issues or submit pull requests if:

* You want to process another team or season
* You need help building analytical models
* You want additional CSV fields or structure

