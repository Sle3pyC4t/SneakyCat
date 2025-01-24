import os
import subprocess
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
    except subprocess.CalledProcessError as e:
        print(f"Error running Gitleaks on {local_dir}: {e}")

if __name__ == "__main__":
    # User input
    search_query = "okx"
    token = input("Enter your GitHub token (or press Enter to skip): ").strip()
    config_path = "./gitleaks.toml"

    base_dir = Path("./cloned_repositories")
    base_dir.mkdir(exist_ok=True)

    scan_results_dir = Path("./scan_results")
    scan_results_dir.mkdir(exist_ok=True)

    # Call the previously written search function
    repositories = search_github_repositories(search_query, token=token)

    if not repositories:
        print("No repositories found.")
    else:
        for repo in repositories:
            repo_name = repo["name"]
            repo_owner = repo["owner"]["login"]
            repo_url = repo["clone_url"]
            local_repo_dir = base_dir / repo_owner / repo_name

            print(f"Processing repository: {repo_name} by {repo_owner}")

            # Clone the repository
            clone_repository(repo_url, str(local_repo_dir))

            # Run Gitleaks scan
            run_gitleaks_scan(str(local_repo_dir), scan_results_dir, repo_owner, repo_name, config_path)

        print("All repositories processed.")
