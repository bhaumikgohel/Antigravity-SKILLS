#!/usr/bin/env python3
"""
Similarity checker for duplicate bug detection.
Compares new bug reports against existing JIRA issues.
"""

import argparse
import json
import re
import math
from difflib import SequenceMatcher
from typing import List, Dict, Tuple


def tokenize(text: str) -> List[str]:
    """Extract alphanumeric tokens from text."""
    return re.findall(r'\b[a-zA-Z0-9]+\b', text.lower())


def cosine_similarity(text1: str, text2: str) -> float:
    """Calculate cosine similarity between two texts."""
    tokens1 = tokenize(text1)
    tokens2 = tokenize(text2)
    
    if not tokens1 or not tokens2:
        return 0.0
    
    # Build vocabulary
    vocab = set(tokens1) | set(tokens2)
    
    # Create vectors
    vec1 = [tokens1.count(word) for word in vocab]
    vec2 = [tokens2.count(word) for word in vocab]
    
    # Calculate cosine similarity
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)


def sequence_similarity(text1: str, text2: str) -> float:
    """Calculate sequence matcher ratio."""
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


def keyword_overlap(summary1: str, summary2: str) -> float:
    """Calculate keyword overlap ratio."""
    tokens1 = set(tokenize(summary1))
    tokens2 = set(tokenize(summary2))
    
    if not tokens1 or not tokens2:
        return 0.0
    
    intersection = tokens1 & tokens2
    union = tokens1 | tokens2
    
    return len(intersection) / len(union)


def calculate_bug_similarity(
    new_bug: Dict,
    existing_bug: Dict,
    weights: Dict[str, float] = None
) -> Tuple[float, Dict]:
    """
    Calculate weighted similarity score between two bugs.
    
    Args:
        new_bug: Dict with 'summary', 'description', 'component'
        existing_bug: Dict with 'summary', 'description', 'component'
        weights: Custom weights for each field
    
    Returns:
        Tuple of (overall_score, breakdown_dict)
    """
    weights = weights or {
        'summary': 0.40,
        'description': 0.40,
        'component': 0.10,
        'steps': 0.10
    }
    
    # Summary similarity (cosine + keyword)
    summary_cos = cosine_similarity(
        new_bug.get('summary', ''),
        existing_bug.get('summary', '')
    )
    summary_key = keyword_overlap(
        new_bug.get('summary', ''),
        existing_bug.get('summary', '')
    )
    summary_sim = (summary_cos + summary_key) / 2
    
    # Description similarity
    desc_sim = cosine_similarity(
        new_bug.get('description', ''),
        existing_bug.get('description', '')
    )
    
    # Component match (binary)
    comp_sim = 1.0 if new_bug.get('component') == existing_bug.get('component') else 0.0
    
    # Steps to reproduce similarity
    steps_sim = sequence_similarity(
        new_bug.get('steps_to_reproduce', ''),
        existing_bug.get('steps_to_reproduce', '')
    )
    
    # Weighted average
    overall = (
        summary_sim * weights['summary'] +
        desc_sim * weights['description'] +
        comp_sim * weights['component'] +
        steps_sim * weights['steps']
    )
    
    breakdown = {
        'summary': round(summary_sim, 3),
        'description': round(desc_sim, 3),
        'component': round(comp_sim, 3),
        'steps': round(steps_sim, 3),
        'overall': round(overall, 3)
    }
    
    return overall, breakdown


def find_duplicates(
    new_bug: Dict,
    candidates: List[Dict],
    threshold: float = 0.70
) -> List[Dict]:
    """
    Find potential duplicates from candidate bugs.
    
    Args:
        new_bug: The new bug to check
        candidates: List of existing bugs
        threshold: Minimum similarity score (0-1)
    
    Returns:
        List of matches sorted by similarity (descending)
    """
    matches = []
    
    for candidate in candidates:
        score, breakdown = calculate_bug_similarity(new_bug, candidate)
        
        if score >= threshold:
            matches.append({
                'key': candidate.get('key', 'UNKNOWN'),
                'summary': candidate.get('summary', ''),
                'similarity': score,
                'breakdown': breakdown,
                'url': candidate.get('url', '')
            })
    
    # Sort by similarity descending
    matches.sort(key=lambda x: x['similarity'], reverse=True)
    return matches


def format_results(matches: List[Dict], threshold_high: float = 0.85) -> str:
    """Format match results for display."""
    if not matches:
        return "✅ No duplicate found - Safe to create new bug ticket."
    
    lines = ["Duplicate Check Results:", "=" * 50]
    
    high_matches = [m for m in matches if m['similarity'] >= threshold_high]
    possible_matches = [m for m in matches if m['similarity'] < threshold_high]
    
    if high_matches:
        lines.append("\n🔴 HIGH PROBABILITY DUPLICATES:")
        for m in high_matches:
            lines.append(f"   • {m['key']}: \"{m['summary'][:50]}...\" ({m['similarity']:.0%} match)")
            lines.append(f"     URL: {m['url']}")
    
    if possible_matches:
        lines.append("\n🟡 POSSIBLE DUPLICATES (Review recommended):")
        for m in possible_matches:
            lines.append(f"   • {m['key']}: \"{m['summary'][:50]}...\" ({m['similarity']:.0%} match)")
    
    # Recommendation
    lines.append("\n📋 Recommendation:")
    if high_matches:
        lines.append(f"   → Review {high_matches[0]['key']} before creating new bug.")
    elif possible_matches:
        lines.append("   → Check possible duplicates or add more details to differentiate.")
    else:
        lines.append("   → No duplicates found. Proceed with ticket creation.")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='Check for duplicate JIRA bugs')
    parser.add_argument('--new-bug', required=True, help='Path to new bug JSON file')
    parser.add_argument('--candidates', required=True, help='Path to candidate bugs JSON file')
    parser.add_argument('--threshold', type=float, default=0.70, help='Similarity threshold (0-1)')
    parser.add_argument('--output', help='Output file path (optional)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # Load data
    with open(args.new_bug, 'r', encoding='utf-8') as f:
        new_bug = json.load(f)
    
    with open(args.candidates, 'r', encoding='utf-8') as f:
        candidates = json.load(f)
    
    # Find duplicates
    matches = find_duplicates(new_bug, candidates, args.threshold)
    
    # Output
    if args.json:
        result = {
            'new_bug_summary': new_bug.get('summary', ''),
            'candidates_checked': len(candidates),
            'matches_found': len(matches),
            'matches': matches
        }
        output = json.dumps(result, indent=2)
    else:
        output = format_results(matches)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
    else:
        print(output)


if __name__ == '__main__':
    main()
