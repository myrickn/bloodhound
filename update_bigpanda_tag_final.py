import argparse
import re
import csv
import os
from datetime import datetime
from getpass import getuser
from datadog import initialize, api

DATADOG_OPTIONS = {
    'api_key': 'YOUR_API_KEY',
    'app_key': 'YOUR_APP_KEY'
}

initialize(**DATADOG_OPTIONS)

BP_TAG_PATTERN = re.compile(r"(BigPandaTags:\s*\[)(.*?)(\])", re.DOTALL)
LOG_DIR = r"C:\BITBUCKET\StrayDog\log"
os.makedirs(LOG_DIR, exist_ok=True)

def load_tag_mappings(file_path, revert=False):
    tag_map = {}
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) == 2:
                old_tag, new_tag = row[0].strip(), row[1].strip()
                if revert:
                    tag_map[new_tag] = old_tag
                else:
                    tag_map[old_tag] = new_tag
    return tag_map

def log_change(log_file, user, monitor_id, name, old_tag, new_tag, old_block, new_block, revert, confirm):
    log_file.write(
        f'timestamp="{datetime.utcnow().isoformat()}" '
        f'user="{user}" '
        f'monitor_id="{monitor_id}" '
        f'monitor_name="{name.replace("\"", "\'")}" '
        f'action="update" '
        f'old_tag="{old_tag}" '
        f'new_tag="{new_tag}" '
        f'old_tags="{old_block.strip()}" '
        f'new_tags="{new_block.strip()}" '
        f'revert_mode="{str(revert).lower()}" '
        f'confirm="{str(confirm).lower()}"\n'
    )

def update_bigpanda_tags(tag_map, confirm=False, revert=False):
    monitors = api.Monitor.get_all()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file_path = os.path.join(LOG_DIR, f"bigpanda_tag_updates_{timestamp}.log")
    user = getuser()
    total_matches = 0
    updated = 0

    with open(log_file_path, "w", encoding="utf-8") as log_file:
        for monitor in monitors:
            if not isinstance(monitor, dict):
                continue

            monitor_id = monitor.get("id")
            name = monitor.get("name", "")
            message = monitor.get("message", "")

            if "@bigpanda-BigPanda-Sandbox" not in message:
                continue

            match = BP_TAG_PATTERN.search(message)
            if not match:
                continue

            tag_block = match.group(2)
            tags = [tag.strip().strip("'\"") for tag in tag_block.split(',')]
            modified = False
            new_tags = []

            for tag in tags:
                if tag in tag_map:
                    new_tags.append(tag_map[tag])
                    log_change(log_file, user, monitor_id, name, tag, tag_map[tag], tag_block, ', '.join(new_tags), revert, confirm)
                    modified = True
                else:
                    new_tags.append(tag)

            if not modified:
                continue

            total_matches += 1
            updated_tags = ', '.join([f"'{t}'" for t in new_tags])
            new_message = message.replace(match.group(0), match.group(1) + updated_tags + match.group(3))

            if confirm:
                full_payload = {
                    'name': monitor['name'],
                    'type': monitor['type'],
                    'query': monitor['query'],
                    'message': new_message,
                    'tags': monitor.get('tags', []),
                    'options': monitor.get('options', {}),
                    'priority': monitor.get('priority'),
                    'restricted_roles': monitor.get('restricted_roles', []),
                    'multi': monitor.get('multi', False),
                    'thresholds': monitor.get('thresholds') if 'thresholds' in monitor else None
                }
                full_payload = {k: v for k, v in full_payload.items() if v is not None}
                api.Monitor.update(monitor_id, **full_payload)
                print(f"Updated Monitor ID {monitor_id}")
                updated += 1
            else:
                print(f"Dry run — Monitor ID {monitor_id} would be updated")

    print(f"\n--- Summary ---")
    print(f"Total Matched: {total_matches}")
    print(f"Total Updated: {updated if confirm else 0}")
    print(f"Log saved to: {log_file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update BigPanda Tags in Datadog monitors.")
    parser.add_argument("csv", help="CSV file with old_tag,new_tag mappings")
    parser.add_argument("--confirm", action="store_true", help="Apply changes (default is dry-run)")
    parser.add_argument("--revert", action="store_true", help="Revert tags (new → old)")
    args = parser.parse_args()

    tag_map = load_tag_mappings(args.csv, revert=args.revert)
    update_bigpanda_tags(tag_map, confirm=args.confirm, revert=args.revert)
