import requests
import json
# END IMPORTS


account_id = ""
client_id = ""
client_secret = ""
access_token_url = "https://oauth.brightcove.com/v4/access_token"
# profiles_base_url = f"https://cms.api.brightcove.com/v1/accounts/{pub_id}"

res = requests.post(access_token_url, params="grant_type=client_credentials", auth=(
    client_id, client_secret))
access_token = res.json().get('access_token')

headers = {'Authorization': 'Bearer ' +
           access_token, "Content-Type": "application/json"}

# url = f"https://cms.api.brightcove.com/v1/accounts/{account_id}/counts/videos"


limit = 20
offset = 0
all_results = []
i = 1
while 1:
    url = (
        f"https://cms.api.brightcove.com/v1/accounts/{account_id}/videos/?limit={limit}&offset={offset}")
    r = requests.get(url, headers=headers)
    data = r.json()
    i += 1
    print(i)
    if not data:
        break
    all_results += data
    offset += 20

formatted_data = []

for result in all_results:
    formatted_data.append({
        'id': result['id'],
        'title': result['name'],
        'description': result['description'],
        'long_description': result['long_description'],
        'duration': result['duration'],
        'url': result['link'],
        'text_tracks': result['text_tracks'],
        'tags': result['tags']
    })


with open('bc_videos_data.json', 'w') as json_file:
    json.dump(formatted_data, json_file, indent=4)
