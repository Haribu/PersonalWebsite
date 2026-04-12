import urllib.request
import json
try:
    url = "https://api.github.com/repos/Haribu/PersonalWebsite/issues?labels=blog-queue&state=open&per_page=100"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    data = json.loads(response.read().decode('utf-8'))
    with open('tmp_test_2.json', 'w') as f:
        json.dump(data, f)
    print("Success, downloaded", len(data), "items")
except Exception as e:
    print(e)
