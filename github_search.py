import requests
import csv

def search_github_repositories(search_query, per_page=1000, page=1, output_file="results.csv", token=None):
    """
    Search GitHub repositories using a search query and save results to a CSV file.

    :param search_query: The string to search for (e.g., "machine learning")
    :param per_page: Number of results per page (default: 10, max: 100)
    :param page: Page number for paginated results (default: 1)
    :param output_file: CSV file to save the search results (default: "results.csv")
    :param token: GitHub personal access token for authentication (default: None)
    :return: A list of repositories matching the query.
    """
    # GitHub Search API URL
    api_url = "https://api.github.com/search/repositories"

    # Set up the query parameters
    params = {
        "q": search_query,
        "per_page": per_page,
        "page": page
    }

    # Set up headers for authentication
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"

    try:
        # Send a GET request to the GitHub API
        response = requests.get(api_url, params=params, headers=headers)

        # Raise an exception if the request was not successful
        response.raise_for_status()

        # Parse the JSON response
        data = response.json()

        # Extract repository information
        repositories = data.get("items", [])

        # Save results to a CSV file
        with open(output_file, mode="w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            # Write the header row
            writer.writerow(["Name", "Owner", "URL", "Stars", "Description"])

            # Write repository information
            for repo in repositories:
                writer.writerow([
                    repo["name"],
                    repo["owner"]["login"],
                    repo["html_url"],
                    repo["stargazers_count"],
                    repo["description"]
                ])

        print(f"Results saved to {output_file}")
        return repositories

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return []

if __name__ == "__main__":
    # User input for the search query
    query = "contracts"
    output_file = "github_search_results.csv"

    # Optional: Provide your GitHub personal access token for authentication
    token = input("Enter your GitHub token (or press Enter to skip): ").strip()

    # Search GitHub repositories
    repositories = search_github_repositories(query, output_file=output_file, token=token)

    # Display results
    if repositories:
        print("\nTop repositories matching your search have been saved to the CSV file.")
    else:
        print("No repositories found for your search query.")
