import requests
import json
from collections import Counter
import os

# The example in the directory was made with geopy/geopy, since it takes a lot of time to process all the informations.

# Get GitHub token from environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise ValueError("Please set the GITHUB_TOKEN environment variable.")

# Headers for GitHub API with the personal access token
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_pull_requests(org, project):
    url = f"https://api.github.com/repos/{org}/{project}/issues"
    params = {"state": "all", "per_page": 100}
    all_pull_requests = []

    # Paginate through all pull requests
    page = 1
    while True:
        params['page'] = page
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        issues = response.json()
        
        # Filter only pull requests from issues
        pull_requests = [issue for issue in issues if 'pull_request' in issue]
        all_pull_requests.extend(pull_requests)
        
        if not issues:
            break
        page += 1

    return all_pull_requests

def find_most_commented_pr(pull_requests):
    # Find pull request with the most comments
    return max(pull_requests, key=lambda pr: pr.get("comments", 0))

def top_commenters(pull_requests, top_n=5):
    commenters = Counter()
    for pr in pull_requests:
        pr_comments_url = pr["comments_url"]
        comments_response = requests.get(pr_comments_url, headers=headers)
        comments_response.raise_for_status()
        comments = comments_response.json()
        
        # Count each commenter
        commenters.update([comment["user"]["login"] for comment in comments])
    
    return commenters.most_common(top_n)

def top_labels(pull_requests, top_n=5):
    labels_counter = Counter()
    label_colors = {}
    for pr in pull_requests:
        for label in pr["labels"]:
            label_name = label["name"]
            labels_counter[label_name] += 1
            label_colors[label_name] = label["color"]
    
    # Get the top labels with their colors
    top_labels = labels_counter.most_common(top_n)
    return [{"name": label, "count": count, "color": label_colors[label]} for label, count in top_labels]

def main():
    org_project = input("Enter the GitHub project in format {org}/{project}: ")
    org, project = org_project.split("/")

    # Step 1: Get all pull requests
    pull_requests = get_pull_requests(org, project)
    print(f"Total pull requests fetched: {len(pull_requests)}")

    # Step 2: Create a big JSON document
    big_json_document = {"pull_requests": pull_requests}
    
    # Write the big JSON document to a file
    with open("pull_requests.json", "w") as file:
        json.dump(big_json_document, file, indent=2)
    print("\nAll pull requests have been written to 'pull_requests.json'.")

    # Step 3: Find the pull request with the most comments
    most_commented_pr = find_most_commented_pr(pull_requests)
    print("\nPull request with the most comments:")
    print(json.dumps(most_commented_pr, indent=2))

    # Step 4: Top 5 commenters
    top_5_commenters = top_commenters(pull_requests)
    print("\nTop 5 Commenters:")
    print(json.dumps(top_5_commenters, indent=2))

    # Step 5: Top 5 labels
    top_5_labels = top_labels(pull_requests)
    print("\nTop 5 Labels:")
    print(json.dumps(top_5_labels, indent=2))

if __name__ == "__main__":
    main()