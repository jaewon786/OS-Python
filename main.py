import requests
import argparse
import matplotlib.pyplot as plt
from collections import defaultdict
from prettytable import PrettyTable
import math

def get_commits(owner, repo, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Error fetching commits:", response.json())
        return {}

    commits = response.json()
    user_commit_count = defaultdict(int)

    for commit in commits:
        author = commit.get("author", {}).get("login")
        if author:
            user_commit_count[author] += 1

    return user_commit_count

def get_issues(owner, repo, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Error fetching issues:", response.json())
        return {}

    issues = response.json()
    user_issue_count = defaultdict(int)

    for issue in issues:
        if "pull_request" in issue:  # PR은 제외
            continue
        author = issue.get("user", {}).get("login")
        if author:
            user_issue_count[author] += 1

    return user_issue_count

def calculate_scores(commits, issues):
    scores = {}
    users = set(commits.keys()).union(set(issues.keys()))

    for user in users:
        commit_count = commits.get(user, 0)
        issue_count = issues.get(user, 0)
        scores[user] = commit_count * 2 + issue_count * 5

    return scores

def display_results(commits, issues, scores):
    table = PrettyTable()
    table.field_names = ["User", "Commits", "Issues", "Score"]
    
    for user, score in scores.items():
        table.add_row([user, commits.get(user, 0), issues.get(user, 0), score])
    
    print(table)

def plot_results(commits, issues, scores):
    sorted_users = sorted(scores.keys(), key=lambda user: scores[user], reverse=True)
    commit_values = [commits.get(user, 0) * 2 for user in sorted_users]  # 커밋 점수
    issue_values = [issues.get(user, 0) * 5 for user in sorted_users]  # 이슈 점수
    
    bar_width = 0.5
    x = range(len(sorted_users))
    
    plt.figure(figsize=(10, 6))
    bars1 = plt.bar(x, commit_values, color="skyblue", label="Commit Score", width=bar_width)
    bars2 = plt.bar(x, issue_values, bottom=commit_values, color="orange", label="Issue Score", width=bar_width)
    
    plt.xlabel("Contributors")
    plt.ylabel("Score")
    plt.title("GitHub Contribution Scores")
    
    # y축 최대값을 최고 점수에 맞추고 5등분하여 설정
    max_score = max(scores.values(), default=0)
    y_max = math.ceil(max_score / 5) * 5  # 5의 배수로 올림
    y_ticks = [i for i in range(0, y_max + 1, max(1, y_max // 5))]
    plt.yticks(y_ticks)
    
    # 막대 위에 총점 표시
    for bar1, bar2, user in zip(bars1, bars2, sorted_users):
        total = bar1.get_height() + bar2.get_height()
        plt.text(bar1.get_x() + bar1.get_width()/2, total, str(scores[user]), ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.xticks(x, sorted_users, rotation=0)
    plt.legend()
    plt.tight_layout()
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="GitHub Repository Contribution Visualizer")
    parser.add_argument("owner", help="GitHub repository owner")
    parser.add_argument("repo", help="GitHub repository name")
    parser.add_argument("token", help="GitHub personal access token")
    parser.add_argument("--graph", action="store_true", help="Display results as a graph instead of a table")
    args = parser.parse_args()

    commits = get_commits(args.owner, args.repo, args.token)
    issues = get_issues(args.owner, args.repo, args.token)
    scores = calculate_scores(commits, issues)
    
    if args.graph:
        plot_results(commits, issues, scores)
    else:
        display_results(commits, issues, scores)

if __name__ == "__main__":
    main()
