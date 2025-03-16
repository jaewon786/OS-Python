import requests
import argparse
from prettytable import PrettyTable

GITHUB_API_URL = "https://api.github.com/repos"
COMMIT_SCORE = 1
ISSUE_SCORE = 3

def get_commits(owner, repo, token):
    url = f"{GITHUB_API_URL}/{owner}/{repo}/commits"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print("Error fetching commits:", response.json())
        return {}
    
    commits = response.json()
    user_commit_count = {}
    
    for commit in commits:
        author = commit.get("author", {}).get("login")
        if author:
            user_commit_count[author] = user_commit_count.get(author, 0) + 1
    
    return user_commit_count

def get_issues(owner, repo, token):
    url = f"{GITHUB_API_URL}/{owner}/{repo}/issues"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print("Error fetching issues:", response.json())
        return {}
    
    issues = response.json()
    user_issue_count = {}
    
    for issue in issues:
        if "pull_request" in issue: 
            continue
        author = issue.get("user", {}).get("login")
        if author:
            user_issue_count[author] = user_issue_count.get(author, 0) + 1
    
    return user_issue_count

def calculate_scores(commits, issues):
    scores = {}
    users = set(commits.keys()).union(set(issues.keys()))
    
    for user in users:
        commit_count = commits.get(user, 0)
        issue_count = issues.get(user, 0)
        scores[user] = commit_count * COMMIT_SCORE + issue_count * ISSUE_SCORE
    
    return scores

def display_results(commits, issues, scores):
    table = PrettyTable()
    table.field_names = ["User", "Commits", "Issues", "Score"]
    
    for user, score in scores.items():
        table.add_row([user, commits.get(user, 0), issues.get(user, 0), score])
    
    print(table)

def main():
    parser = argparse.ArgumentParser(description="GitHub Repository Contribution Score Calculator")
    parser.add_argument("owner", help="GitHub repository owner")
    parser.add_argument("repo", help="GitHub repository name")
    parser.add_argument("token", help="GitHub toekn")
    args = parser.parse_args()
    
    commits = get_commits(args.owner, args.repo, args.token)
    issues = get_issues(args.owner, args.repo, args.token)
    scores = calculate_scores(commits, issues)
    display_results(commits, issues, scores)

if __name__ == "__main__":
    main()