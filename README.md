# 🐼 BigPanda Tag Management Tools for Datadog

This repository contains two scripts that help manage `BigPandaTags` embedded in Datadog monitor messages:

- `export_bigpanda_tags.py`: Exports a list of monitors with their `BigPandaTags` to a CSV file.
- `update_bigpanda_tag_final.py`: Updates `BigPandaTags` in Datadog monitor messages based on mappings provided in a CSV.

---

## 📁 Prerequisites

- Python 3.7+
- Datadog API credentials with permission to read/write monitors
- Install the Datadog Python module:

```bash
pip install datadog
```

---

## 🔐 API Keys

Both scripts require valid Datadog API and APP keys. These are hardcoded in the current scripts under:

```python
options = {
    'api_key': 'YOUR_API_KEY',
    'app_key': 'YOUR_APP_KEY'
}
```

Update them as needed.

---

## 📤 `export_bigpanda_tags.py`

### 🔍 Description

Scans all monitors in Datadog and extracts any `BigPandaTags` blocks from their messages **if** the message contains `@bigpanda-BigPanda-Sandbox` can be edited to `@bigpanda-BigPanda-Production`.

### 📦 Output

- A CSV file called `bigpanda_monitors_with_tags.csv` containing:
  - `name`: The name of the monitor
  - `tags`: The list of tags extracted from `BigPandaTags`

### ▶️ Usage

```bash
python export_bigpanda_tags.py
```

---

## ✏️ `update_bigpanda_tag_final.py`

### 🔍 Description

Updates `BigPandaTags` in Datadog monitors using a CSV mapping file. It supports dry-run mode by default and will only perform real updates if the `--confirm` flag is used.

### 📄 CSV Format

```csv
old_tag,new_tag
team-old,team-new
env-prod,env-production
```

Use the `--revert` flag to reverse the mapping (`new_tag → old_tag`).

### 📂 Logging

A log file is saved to:

```text
C:\bloodhound\log\bigpanda_tag_updates_<timestamp>.log
```

Log entries include:
- User name
- Timestamp
- Monitor ID and name
- Tags before and after the update
- Revert and confirm flags

### ▶️ Usage

```bash
# Dry run (default)
python update_bigpanda_tag_final.py tag_map.csv

# Confirmed update
python update_bigpanda_tag_final.py tag_map.csv --confirm

# Revert mode (new → old) in dry run
python update_bigpanda_tag_final.py tag_map.csv --revert

# Confirmed revert
python update_bigpanda_tag_final.py tag_map.csv --revert --confirm
```

---

## 🛠 Use Case Example

1. Export your current BigPandaTags for review:
   ```bash
   python export_bigpanda_tags.py
   ```

2. Prepare a `tag_map.csv` file with desired changes.

3. Test changes with a dry run:
   ```bash
   python update_bigpanda_tag_final.py tag_map.csv
   ```

4. If output looks good, confirm changes:
   ```bash
   python update_bigpanda_tag_final.py tag_map.csv --confirm
   ```

5. If needed, roll back:
   ```bash
   python update_bigpanda_tag_final.py tag_map.csv --revert --confirm
   ```

---
