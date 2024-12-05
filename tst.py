import requests

print(requests.get("http://admin:admin@localhost:3000/api/search").text)