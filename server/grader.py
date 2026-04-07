import re
from typing import List
from models import CodeReviewAction, CodeReviewState

class DeterministicGrader:
    def evaluate(self, state: CodeReviewState, action: CodeReviewAction) -> float:
        if not action.comments and action.decision == "approve":
            if state.known_issues:
                return 0.0 # Missed issues
            else:
                return 1.0 # Correctly approved clean code
        
        # We look for keywords in the comments to match known issues
        found_issues = 0
        total_known_issues = len(state.known_issues)
        
        if total_known_issues == 0:
            if action.decision == "request_changes" or action.comments:
                return 0.0 # False positive penalty
            return 1.0

        combined_comments = " ".join([c.issue.lower() for c in action.comments])
        
        # simple keyword matching
        matched_issues = set()
        for issue in state.known_issues:
            if issue.lower() in combined_comments:
                matched_issues.add(issue)
            else:
                # Check individual words as a fallback
                words = issue.lower().split()
                if all(w in combined_comments for w in words):
                    matched_issues.add(issue)
                     
        # Some issues might be aliases for the same underlying problem.
        # But for strict deterministic scoring, let's treat any matched known_issue as progress.
        # Max score shouldn't exceed 1.0.
        found_issues = len(matched_issues)
        base_score = min(1.0, float(found_issues) / max(1.0, float(total_known_issues / 2))) # Suppose finding half the keywords is perfect.
        # Wait, if there are multiple keywords for the same flaw, we should just match at least one.
        
        has_found_flaw = found_issues > 0
        
        score = 0.0
        if has_found_flaw:
            score = 1.0
            
        # Penalize false positives (excessive comments not matching known issues)
        if len(action.comments) > 3: # arbitrary threshold for simple code snippets
            penalty = (len(action.comments) - 3) * 0.1
            score = max(0.0, score - penalty)
            
        # Ensure decision aligns
        if action.decision == "approve" and has_found_flaw:
            score = max(0.0, score - 0.5)
            
        if action.decision == "request_changes" and not has_found_flaw:
            return 0.0 # Requested changes but didn't state the right issue
            
        return round(score, 2)