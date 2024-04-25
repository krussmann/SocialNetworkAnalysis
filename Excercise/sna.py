from graph import Graph
from mastodon import MastodonCrawler
import graphviz
import os
import sys

def main():
    if(len(sys.argv)<3):
        print('Usage: sna.py <mastodon_id> <analysis_id>')
        print('example:')
        print('sna.py 31622 0')
        return
    mastodon_id = sys.argv[1]
    analysis_id = int(sys.argv[2])
    if analysis_id in [2,4]:
        payload = sys.argv[3]

    match analysis_id:
        case 0:
            print("Fetching real-world data from Mastodon API...")
            c = MastodonCrawler()
            network, path = c.fetch_network_dict(mastodon_id)

            print("Parsing Mastodon data to Graph object...")
            g = Graph()
            # g.parse_data(filepath='ressources/network_anonym.json')
            g.parse_data(filepath=path)

            print_banner("Exercise 1.1: Graph implementation", "-")
            print("Creating network visualization...")
            g.show("network")
        case 1:
            g = load_network(mastodon_id)
            print_banner("Exercise 1.2: Network Connectivity (based on DFS)", "-")
            subgraphs = g.get_subgraphs()
            status = "connected" if len(subgraphs) == 1 else "disconnected"
            print(f"Our {status} network consists of {len(subgraphs)} {status} " +
                  f"{'subgraph' if len(subgraphs) == 1 else 'subgraphs'}.\n")
        case 2:
            g = load_network(mastodon_id)
            try:
                user1, user2 = payload.split('-')
            except:
                sys.exit("Payload should be 2 users connected with a single dash in the format of a string 'user1-user2'.")
            print_banner("Exercise 1.3: Shortest Path (based on BFS with path tracking)", "-")
            print(f"Received values: {user1} and {user2}")
            shortest_path = g.shortest_path(user1, user2)
            if shortest_path:
                print(f"The shortest_path between {user1} and {user2} is {shortest_path}.\n")
            else:
                print(f"There exists no connection between {user1} and {user2}.\n")
        case 3:
            g = load_network(mastodon_id)
            print_banner("Exercise 1.4: Most Influential User (based on Closeness-measure)", "-")
            mip, min_avg_length = g.most_influential()
            print(
                f"{mip} is the most influential person in the network with an avg shortest path length of {min_avg_length} to all other users.\n")
            # Optionally: let self.most_influential() print out the average length of all average shortest path lengths.
        case 4:
            g = load_network(mastodon_id)
            print_banner("Exercise 1.5: Community Detection (based on Girvan Newman Algorithm)", "-")
            try:
                payload = int(payload)
            except ValueError:
                assert False, "payload should be an integer."

            # Remove already existing clusters of single users
            remove = [i[0] for i in g.get_subgraphs() if len(i) == 1]
            for user in remove:
                g.remove_vertex(user)

            # ignore clusters of single users:
            multi_clusters_only = False
            while not multi_clusters_only:
                communities = g.girvan_newman_algorithm(clusters=payload)
                remove = [users[0] for users in communities if len(users) == 1]
                for user in remove:
                    g.remove_vertex(user)
                communities = [com for com in communities if len(com) > 1]
                if len(communities) == payload:
                    multi_clusters_only = True

            # communities = g.girvan_newman_algorithm(clusters=payload)
            print(f"For n = {payload} clusters, the Girvan Newman algorithm detected the following communities:")
            for i, c in enumerate(communities, 1):
                print(f"\tCommunity {i} - {c}")

            print("Creating final visualization with identified communities...")
            g.show("network_communities")


def print_banner(text: str, symbol: str = "="):
    print(symbol * len(text))
    print(text)
    print(symbol * len(text))

def load_network(mastodon_id):
    g = Graph()
    g.parse_data(f"ressources/network_{mastodon_id}.json")
    # g.show("anonymize")
    return g

if __name__ == '__main__':
    main()