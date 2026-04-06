import requests

url = "https://api.investing.com/api/financialdata/historical/945883?start-date=2024-01-01&end-date=2026-04-06&time-frame=Daily"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.investing.com/",
    "Origin": "https://www.investing.com",
    "Accept": "application/json"
}

response = requests.get(url, headers=headers)
print(response.status_code)
print(response.json())
