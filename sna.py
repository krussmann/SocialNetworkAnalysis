from graph import Graph
from mastodon import MastodonCrawler
import sys

def main():
    # Check if correct number of command-line arguments is provided
    if(len(sys.argv)<3):
        print('Usage: sna.py <mastodon_id> <analysis_id>')
        print('Example:')
        print('sna.py 31622 0')
        return

    # Parse command-line arguments
    mastodon_id = sys.argv[1]
    analysis_id = int(sys.argv[2])

    # Additional payload required for specific analysis IDs
    if analysis_id in [2,4]:
        payload = sys.argv[3]

    # Perform actions based on analysis_id
    match analysis_id:
        case 0:
            print("Fetching real-world data from Mastodon API...")
            c = MastodonCrawler()
            network, path = c.fetch_network_dict(mastodon_id)

            print("Parsing Mastodon data into a Graph object...")
            graph = Graph()
            graph.parse_data(filepath=path)

            print_banner("Exercise 1.1: Graph implementation", "-")
            print("Creating network visualization...")
            graph.show("network")

        case 1:
            # Load network data from file
            graph = load_network(mastodon_id)
            print_banner("Exercise 1.2: Network Connectivity (based on DFS)", "-")
            subgraphs = graph.get_subgraphs()
            status = "connected" if len(subgraphs) == 1 else "disconnected"
            print(f"Our {status} network consists of {len(subgraphs)} {status} " +
                  f"{'subgraph' if len(subgraphs) == 1 else 'subgraphs'}.\n")

        case 2:
            # Load network data from file
            graph = load_network(mastodon_id)
            try:
                user1, user2 = payload.split('-')
            except:
                sys.exit("Payload should be 2 users connected with a single dash in the format of a string 'user1-user2'.")
            print_banner("Exercise 1.3: Shortest Path (based on BFS with path tracking)", "-")
            print(f"Received values: {user1} and {user2}")
            shortest_path = graph.shortest_path(user1, user2)
            if shortest_path:
                print(f"The shortest_path between {user1} and {user2} is {shortest_path}.\n")
            else:
                print(f"There exists no connection between {user1} and {user2}.\n")

        case 3:
            # Load network data from file
            graph = load_network(mastodon_id)

            print_banner("Exercise 1.4: Most Influential User (based on Closeness-measure)", "-")
            mip, min_avg_length = graph.most_influential()
            print(
                f"{mip} is the most influential person in the network with an avg shortest path length of {min_avg_length} to all other users.\n")
            # Optionally: let self.most_influential() print out the average length of all average shortest path lengths.

        case 4:
            # Load network data from file
            graph = load_network(mastodon_id)

            print_banner("Exercise 1.5: Community Detection (based on Girvan Newman Algorithm)", "-")
            try:
                payload = int(payload)
            except ValueError:
                sys.exit("Payload should be an integer.")

            # Remove already existing clusters of single users
            remove = [i[0] for i in graph.get_subgraphs() if len(i) == 1]
            for user in remove:
                graph.remove_vertex(user)

            # Ignore clusters of single users:
            multi_clusters_only = False
            while not multi_clusters_only:
                communities = graph.girvan_newman_algorithm(clusters=payload)
                remove = [users[0] for users in communities if len(users) == 1]
                for user in remove:
                    graph.remove_vertex(user)
                communities = [com for com in communities if len(com) > 1]
                if len(communities) == payload:
                    multi_clusters_only = True

            print(f"For n = {payload} clusters, the Girvan Newman algorithm detected the following communities:")
            for i, c in enumerate(communities, 1):
                print(f"\tCommunity {i} - {c}")

            print("Creating final visualization with identified communities...")
            graph.show("network_communities")


def print_banner(text: str, symbol: str = "="):
    """Utility function to print a banner with specified text."""
    print(symbol * len(text))
    print(text)
    print(symbol * len(text))

def load_network(mastodon_id):
    """Load network data from a JSON file."""
    g = Graph()
    g.parse_data(f"ressources/network_{mastodon_id}.json")
    return g

if __name__ == '__main__':
    main()