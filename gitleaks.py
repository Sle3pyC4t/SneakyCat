import json
import os
import subprocess
import csv
from pathlib import Path
from github_search import search_github_repositories

def clone_repository(repo_url, local_dir):
    """
    Clone a GitHub repository to a local directory.

    :param repo_url: The URL of the GitHub repository.
    :param local_dir: The directory to clone the repository into.
    """
    try:
        subprocess.run(["git", "clone", repo_url, local_dir], check=True)
        print(f"Cloned {repo_url} into {local_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository {repo_url}: {e}")

def run_gitleaks_scan(local_dir, output_dir, repo_owner, repo_name, config_path):
    """
    Run Gitleaks scan on a local repository with a specified configuration file.

    :param local_dir: The local directory of the cloned repository.
    :param output_dir: The base directory to save Gitleaks scan results.
    :param repo_owner: The owner of the repository.
    :param repo_name: The name of the repository.
    :param config_path: The path to the Gitleaks configuration file.
    """
    output_path = Path(output_dir) / repo_owner / repo_name
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / "gitleaks_report.json"

    try:
        subprocess.run([
            "gitleaks", "detect", "--source", local_dir,
            "--config", config_path,
            "--report-path", str(output_file)
        ])
        print(f"Scan completed for {local_dir}, results saved to {output_file}")
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"Error running Gitleaks on {local_dir}: {e}")
        return None

def filter_scan_results(scan_file, repo_url):
    """
    Filter Gitleaks scan results and return significant findings.

    :param scan_file: Path to the Gitleaks scan result file.
    :param repo_url: URL of the GitHub repository.
    :return: List of filtered findings with repository link.
    """
    filtered_results = []
    try:
        raw_results = json.load(open(scan_file))
        for item in raw_results:
            if "test" in item['File'].lower() or "example" in item['File'].lower():
                continue
            permlink = f"{repo_url}/blob/{item['Commit']}/{item['File']}#L{item['StartLine']}C{item['StartColumn']}-L{item['EndLine']}C{item['EndColumn']}"
            filtered_results.append({"finding": item['RuleID'], "repo_url": permlink})
            print(f"Finding: {item['RuleID']}, Link: {permlink}")
    except FileNotFoundError:
        print(f"Scan file {scan_file} not found.")

    return filtered_results

def save_filtered_results(filtered_results, output_csv):
    """
    Save filtered results to a CSV file.

    :param filtered_results: List of filtered findings.
    :param output_csv: Path to the output CSV file.
    """
    file_exists = os.path.isfile(output_csv)

    with open(output_csv, mode="a", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["finding", "repo_url"])
        if not file_exists:
            writer.writeheader()
        writer.writerows(filtered_results)

if __name__ == "__main__":
    # User input
    search_query = "tradebot pushed:>2025-01-01 "
    token = input("Enter your GitHub token (or press Enter to skip): ").strip()
    config_path = "./gitleaks.toml"

    base_dir = Path("./cloned_repositories")
    base_dir.mkdir(exist_ok=True)

    scan_results_dir = Path("./scan_results")
    scan_results_dir.mkdir(exist_ok=True)

    filtered_results_csv = "filtered_results.csv"

    # Call the previously written search function
    repositories = search_github_repositories(search_query, token=token)

    if not repositories:
        print("No repositories found.")
    else:
        for repo in repositories:
            repo_name = repo["name"]
            repo_owner = repo["owner"]["login"]
            repo_url = repo["clone_url"]
            github_url = f"https://github.com/{repo_owner}/{repo_name}"
            local_repo_dir = base_dir / repo_owner / repo_name

            print(f"Processing repository: {repo_name} by {repo_owner}")

            # Clone the repository
            clone_repository(repo_url, str(local_repo_dir))

            # Run Gitleaks scan
            scan_file = run_gitleaks_scan(str(local_repo_dir), scan_results_dir, repo_owner, repo_name, config_path)

            if scan_file:
                # Filter scan results
                filtered = filter_scan_results(scan_file, github_url)

                # Save filtered results to CSV
                save_filtered_results(filtered, filtered_results_csv)

        print("All repositories processed.")
