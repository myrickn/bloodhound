from datadog import initialize, api
import re
import csv


options = {
    'api_key': 'YOUR_API_Key',
    'app_key': 'YOUR_APP_Key'
}

initialize(**options)


monitors = api.Monitor.get_all()


bp_tag_pattern = re.compile(r"BigPandaTags:\s*\[(.*?)\]", re.DOTALL)

filtered_monitors = []

for monitor in monitors:
   
    if not isinstance(monitor, dict):
        continue

    name = monitor.get('name', '')
    message = monitor.get('message', '')

   
    if '@bigpanda-BigPanda-Sandbox' in message:
        match = bp_tag_pattern.search(message)
        if match:
            tag_block = match.group(1)
            tags = [tag.strip().strip("'\"") for tag in tag_block.split(',')]
        else:
            tags = []

        filtered_monitors.append({
            'name': name,
            'tags': ', '.join(tags)
        })


with open('bigpanda_monitors_with_tags.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['name', 'tags'])
    writer.writeheader()
    for row in filtered_monitors:
        writer.writerow(row)

print("Export complete: bigpanda_monitors_with_tags.csv")
