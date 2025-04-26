
import requests

CLIENT_ID = '40247'
CLIENT_SECRET = '1nVZjKGDF9OJyMCI5YDhuqF18FJ2CVb5Yfekgd86'

def get_access_token():
    token_resp = requests.post('https://osu.ppy.sh/oauth/token', json={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials',
        'scope': 'public'
    })
    return token_resp.json()['access_token']

def get_recent_scores(username, token):
    headers = {'Authorization': f'Bearer {token}'}
    url = f'https://osu.ppy.sh/api/v2/users/{username}/scores/recent?limit=5&include_fails=1'
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"Error: {resp.status_code} - {resp.text}")
        return []
    return resp.json()

def main():
    print("osu! Recent Score ID Fetcher")
    username = input("Enter your osu! username: ").strip()
    print("Getting access token...")
    token = get_access_token()
    print(f"Getting recent scores for {username}...")
    scores = get_recent_scores(username, token)
    print("\n--- Recent Score IDs ---")
    for score in scores:
        title = score['beatmap']['title']
        pp = score.get('pp', 'N/A')
        print(f"Score ID: {score['id']} | Beatmap: {title} | PP: {pp}")

if __name__ == "__main__":
    main()
