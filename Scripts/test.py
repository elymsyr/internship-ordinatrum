import requests, re
from keys import API_KEY

def find_key(data, key_to_find):
    found_items = []

    def recurse(item, title = None):
        if title == None: title = item['title']
        if isinstance(item, dict):
            # If the item is a dictionary, check for the key and recurse
            if key_to_find in item:
                # If the key is found, add the key-value pair along with the current path
                cleaned_value = re.sub(r'\s+', '', str(item[key_to_find]))
                found_items.append({
                    key_to_find: cleaned_value,
                    'title': title
                })
                return
            # Recurse into the dictionary's values
            for _, value in item.items():
                recurse(value, title=title)
        elif isinstance(item, list):
            for sub_item in item:
                recurse(sub_item, title=title)

    recurse(data)
    return found_items

grafana_url = "https://admin:admin@localhost:3000/api/dashboards/uid/a77c9b13db5d7b"
headers = {'Authorization': f"Bearer {API_KEY}"}
response = requests.get(grafana_url, headers=headers)
dashboard_data = response.json()

queries = dashboard_data['dashboard']['panels']
print(len(queries))
found_queries = []
for row in queries: found_queries.append(find_key(row, 'expr'))


prometheus_url = "http://localhost:9090/api/v1/query"
prometheus_data = []

for query_list in found_queries:
    for query in query_list:
        query_url = f"{prometheus_url}?query={query['expr']}"
        prom_response = requests.get(query_url)
        prom_data = prom_response.json()
        prom_data['query_send'] = query['expr']
        prometheus_data.append({query['title']: prom_data})

with open('test.txt', '+w'):
    for row in prometheus_data:
        with open('test.txt', '+a') as file:
            for key, value in row.items():
                file.writelines(f"{key}: {value}")
                file.writelines('\n')
