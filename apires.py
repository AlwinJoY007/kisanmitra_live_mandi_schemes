import requests

url = "https://api.data.gov.in/resource/35985678-0d79-46b4-9ed6-6f13308a1d24?api-key=579b464db66ec23bdd000001c3a2b22b42ed4c0963388507a8b22a65&format=json&limit=35"
response = requests.get(url)
data = response.json()
print(data)  # <-- inspect the structure
