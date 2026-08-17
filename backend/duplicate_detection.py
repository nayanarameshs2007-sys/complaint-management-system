"""
Duplicate Complaint Detection Module
Calculates word overlap & text similarity percentage between existing complaints and a new submission.
"""
import re
from typing import List, Optional, Tuple

def normalize_text(text: str) -> set:
    """Cleans text into a set of lowercased words (ignoring short stopwords)."""
    words = re.findall(r'\w+', text.lower())
    stopwords = {"a", "an", "the", "is", "at", "near", "of", "in", "on", "and", "or", "to", "there", "has", "have", "by", "with", "this", "that"}
    return {w for w in words if w not in stopwords and len(w) > 2}

def calculate_similarity(text1: str, text2: str) -> int:
    """Calculates Jaccard similarity percentage between two texts."""
    words1 = normalize_text(text1)
    words2 = normalize_text(text2)

    if not words1 or not words2:
        return 0

    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    score = (len(intersection) / len(union)) * 100
    return int(score)

def find_possible_duplicate(new_description: str, new_location: str, existing_complaints: List[dict], threshold: int = 40) -> Tuple[Optional[str], int]:
    """
    Compares a new complaint against existing complaints.
    Returns (duplicate_complaint_id, similarity_score_percentage) if above threshold.
    """
    best_match_id = None
    highest_score = 0

    new_full_text = f"{new_description} {new_location}"

    for item in existing_complaints:
        existing_full_text = f"{item['description']} {item['location']}"
        score = calculate_similarity(new_full_text, existing_full_text)

        if score > highest_score:
            highest_score = score
            best_match_id = item['complaint_id']

    if highest_score >= threshold:
        return best_match_id, highest_score

    return None, 0
