#!/usr/bin/env python3

import matplotlib.pyplot as plt
from prettytable import PrettyTable
import requests
import re
import pandas as pd
from typing import Dict

class RepoAnalyzer:
    """Class to analyze repository participation for scoring"""
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.participants: Dict = {}
        self.score_weights = {
            'commits': 0.4,
            'issues_created': 0.3,
            'issue_comments': 0.3
        }
        
        match = re.match(r"https://github\.com/([^/]+)/([^/]+)", repo_path)
        if not match:
            raise ValueError("Invalid GitHub repository URL format. Expected format: https://github.com/owner/repo")
        
        self.repo_owner, self.repo_name = match.groups()

    def collect_commits(self) -> None:
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/commits"
        response = requests.get(url)
        
        if response.status_code != 200:
            print("Error fetching commits:", response.json())
            return {}
        
        commits = response.json()
        for commit in commits:
            author = commit.get("author")
            if author:
                username = author["login"]
                if username not in self.participants:
                    self.participants[username] = {"commits": 0}
                self.participants[username]["commits"] += 1

    def collect_issues(self) -> None:
        """Collect issues and comments data"""
        # Placeholder for GitHub API integration
        pass

    def calculate_scores(self) -> Dict:
        """Calculate participation scores for each contributor"""
        scores = {}
        for participant, activities in self.participants.items():
            total_score = (
                activities.get('commits', 0) * self.score_weights['commits']
                # + activities.get('issues_created', 0) * self.score_weights['issues_created'] +
                # activities.get('issue_comments', 0) * self.score_weights['issue_comments']
            )
            scores[participant] = round(total_score, 2)
        return scores

    # def generate_table(self, scores: Dict) -> pd.DataFrame:
    #     """Generate a table of participation scores"""
    #     df = pd.DataFrame.from_dict(scores, orient='index', columns=['Score'])
    #     return df
    def generate_table(self, scores: Dict):
        """Generate and print a table of participation scores using PrettyTable"""
        
        table = PrettyTable()
        table.field_names = ["User", "Commit", "Issue", "Score"]
    
        for user, score in scores.items():
            commit_count = self.participants.get(user, {}).get("commits", 0)
            issue_count = self.participants.get(user, {}).get("issues_created", 0)
            table.add_row([user, commit_count, issue_count, round(score, 2)])
        return table

    def generate_chart(self, scores: Dict) -> None:
        """Generate a visualization of participation scores"""
        plt.figure(figsize=(10, 6))
        plt.bar(scores.keys(), scores.values())
        plt.xticks(rotation=45)
        plt.ylabel('Participation Score')
        plt.title('Repository Participation Scores')
        plt.tight_layout()
        plt.savefig('participation_chart.png')
