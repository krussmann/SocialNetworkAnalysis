import requests
import json
import sys
import os
import time

class MastodonCrawler():
    def __init__(self):
        self.g = {} # Graph representation as a dictionary
        self.path = '' # Path to save the network data

    def paginate(self, url):
        followers = set()
        while url:
            # Check if API_key is provided as an environment variable
            if "API_key" not in os.environ:
                sys.exit("Missing API_key environment variable")

            # Make API request with authentication
            response = requests.get(url, headers={'Authorization':f'Bearer {os.environ["API_key"]}'})
            objects = json.loads(response.text) # Convert JSON response to Python list of dictionaries
            users = set([(i['id'],i['username']) for i in objects])
            followers |= users

            # Pagination: get next page URL from response links
            url = response.links['next']['url'] if 'next' in response.links else None
            time.sleep(.5) # Add delay to avoid API rate limiting

        return followers


    def fetch_followers(self, user_id):
        # Fetch followers of a specified user_id
        url = f"https://mastodon.social/api/v1/accounts/{user_id}/followers?limit=80"
        followers = self.paginate(url)
        return followers


    def fetch_network_dict(self, user_id):
        self.path = f'ressources/network_{user_id}.json'
        followers = self.fetch_followers(user_id)
        nodes = list(followers)

        # Prompt user to confirm continuation
        cont = input(f"Found {len(nodes)} followers for the user id {user_id}\n Do you want to continue? (Y/N) ").lower()
        if cont != "y":
            sys.exit(0)

        # Iterate over each follower to fetch their followers
        print(f"Iterating over {len(nodes)} users")
        for i, (id, username) in enumerate(nodes, 1):
            followers = self.fetch_followers(id)
            followers = [f for f in followers if f[0] in [node[0] for node in nodes]]  # Filter shared followers
            print(f"\t user {i+1}/{len(nodes)} {username}({id}) - fetched {len(followers)} shared followers")
            self.g[username] = [f[1] for f in followers]

        # Make graph undirected by adding reverse connections
        for user, items in self.g.items():
            for follower in items:
                if follower in self.g and user not in self.g[follower]:
                        self.g[follower].append(user)

        # Save graph as JSON to specified path
        with open(self.path, 'w') as fp:
            json.dump(self.g, fp)

        return self.g, self.path


if __name__ == '__main__':
    mastodon_id = 0
    c = MastodonCrawler()
    graph, save_path = c.fetch_network_dict(user_id=mastodon_id)









