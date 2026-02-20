#!/usr/bin/env python3
"""
UI Content Validator
Extracts and validates text content from web pages or screenshots.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse


@dataclass
class ValidationIssue:
    severity: str  # critical, major, minor
    category: str  # spelling, grammar, format, terminology, casing
    message: str
    location: str
    current_text: str
    suggested_text: str
    line_number: Optional[int] = None


class ContentExtractor:
    """Extract text content from various sources."""
    
    def from_url(self, url: str) -> Dict[str, str]:
        """Extract text from web page using Playwright."""
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(url)
                
                content = {
                    'url': url,
                    'title': page.title(),
                    'headings': self._extract_headings(page),
                    'buttons': self._extract_buttons(page),
                    'labels': self._extract_labels(page),
                    'errors': self._extract_errors(page),
                    'body_text': page.inner_text('body')
                }
                
                browser.close()
                return content
        except ImportError:
            raise ImportError("Install playwright: pip install playwright")
    
    def _extract_headings(self, page) -> List[str]:
        headings = []
        for level in range(1, 7):
            elements = page.query_selector_all(f'h{level}')
            for el in elements:
                text = el.inner_text().strip()
                if text:
                    headings.append(text)
        return headings
    
    def _extract_buttons(self, page) -> List[str]:
        selectors = ['button', '[role="button"]', 'input[type="submit"]', 'input[type="button"]']
        buttons = []
        for selector in selectors:
            elements = page.query_selector_all(selector)
            for el in elements:
                text = el.inner_text().strip() or el.get_attribute('value') or ''
                if text:
                    buttons.append(text)
        return buttons
    
    def _extract_labels(self, page) -> List[str]:
        labels = []
        elements = page.query_selector_all('label, .label, [class*="label"]')
        for el in elements:
            text = el.inner_text().strip()
            if text:
                labels.append(text)
        return labels
    
    def _extract_errors(self, page) -> List[str]:
        selectors = ['.error', '.alert-danger', '[role="alert"]', '.text-danger']
        errors = []
        for selector in selectors:
            elements = page.query_selector_all(selector)
            for el in elements:
                text = el.inner_text().strip()
                if text:
                    errors.append(text)
        return errors
    
    def from_screenshot(self, image_path: str) -> str:
        """Extract text from screenshot using OCR."""
        try:
            import pytesseract
            from PIL import Image
            
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return {'screenshot': image_path, 'body_text': text}
        except ImportError:
            raise ImportError("Install pytesseract and Pillow: pip install pytesseract Pillow")


class ContentValidator:
    """Validates extracted content against rules."""
    
    def __init__(self, glossary: Dict, rules: Dict):
        self.glossary = glossary
        self.rules = rules
        self.issues: List[ValidationIssue] = []
        
        # Common spelling errors
        self.common_misspellings = {
            'recieve': 'receive',
            'seperate': 'separate',
            'occured': 'occurred',
            'accomodate': 'accommodate',
            'definately': 'definitely',
            'occurence': 'occurrence',
            'refering': 'referring',
            'sucessful': 'successful',
            'untill': 'until',
            'wich': 'which'
        }
    
    def validate(self, content: Dict[str, str]) -> List[ValidationIssue]:
        """Run all validation checks."""
        self.issues = []
        
        all_text = content.get('body_text', '')
        
        # Check spelling
        self._check_spelling(all_text)
        
        # Check terminology
        self._check_terminology(all_text)
        
        # Check formatting
        self._check_currency_format(all_text)
        self._check_date_format(all_text)
        
        # Check casing on specific elements
        for heading in content.get('headings', []):
            self._check_casing(heading, 'heading', 'title')
        
        for button in content.get('buttons', []):
            self._check_casing(button, 'button', 'title')
        
        for label in content.get('labels', []):
            self._check_casing(label, 'label', 'sentence')
        
        # Check grammar patterns
        self._check_grammar_patterns(all_text)
        
        return self.issues
    
    def _check_spelling(self, text: str):
        """Check for common misspellings."""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        for word in words:
            if word in self.common_misspellings:
                self.issues.append(ValidationIssue(
                    severity='major',
                    category='spelling',
                    message=f"Common misspelling detected",
                    location='body text',
                    current_text=word,
                    suggested_text=self.common_misspellings[word]
                ))
    
    def _check_terminology(self, text: str):
        """Check against preferred terminology."""
        preferred = self.glossary.get('preferred_terms', {})
        
        text_lower = text.lower()
        for correct_term, incorrect_terms in preferred.items():
            for incorrect in incorrect_terms:
                pattern = r'\b' + re.escape(incorrect) + r'\b'
                if re.search(pattern, text_lower):
                    self.issues.append(ValidationIssue(
                        severity='major',
                        category='terminology',
                        message=f"Non-preferred term found",
                        location='body text',
                        current_text=incorrect,
                        suggested_text=correct_term
                    ))
    
    def _check_currency_format(self, text: str):
        """Validate currency formatting."""
        # Find currency patterns
        currency_patterns = [
            r'\$\d+\.\d{2}',  # $99.99
            r'USD\s+\d+',     # USD 99
            r'\d+\.\d{2}\s*\$',  # 99.99$ (incorrect)
        ]
        
        expected_format = self.rules.get('format_rules', {}).get('currency', '$#.##')
        
        # Check for malformed currency
        malformed = re.findall(r'\d+\.\d{2}\s*\$', text)  # e.g., "99.99$"
        for match in malformed:
            self.issues.append(ValidationIssue(
                severity='critical',
                category='format',
                message=f"Incorrect currency format",
                location='body text',
                current_text=match,
                suggested_text=f"${match.replace('$', '').strip()}"
            ))
        
        # Check for inconsistent decimal places
        prices = re.findall(r'\$(\d+\.\d+)', text)
        decimal_lengths = set(len(p.split('.')[1]) for p in prices)
        if len(decimal_lengths) > 1:
            self.issues.append(ValidationIssue(
                severity='major',
                category='format',
                message=f"Inconsistent decimal places in prices",
                location='body text',
                current_text=f"Mixed: {prices}",
                suggested_text="Use consistent 2 decimal places"
            ))
    
    def _check_date_format(self, text: str):
        """Validate date formatting consistency."""
        date_patterns = {
            'MM/DD/YYYY': r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            'DD-MM-YYYY': r'\b\d{1,2}-\d{1,2}-\d{4}\b',
            'YYYY-MM-DD': r'\b\d{4}-\d{2}-\d{2}\b',
            'MMM DD, YYYY': r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}, \d{4}\b'
        }
        
        expected_format = self.rules.get('format_rules', {}).get('date', 'MM/DD/YYYY')
        
        found_formats = []
        for format_name, pattern in date_patterns.items():
            if re.search(pattern, text):
                found_formats.append(format_name)
        
        if len(found_formats) > 1:
            self.issues.append(ValidationIssue(
                severity='minor',
                category='format',
                message=f"Inconsistent date formats detected",
                location='body text',
                current_text=f"Found: {', '.join(found_formats)}",
                suggested_text=f"Use consistent '{expected_format}' format"
            ))
    
    def _check_casing(self, text: str, element_type: str, expected_case: str):
        """Check text casing."""
        if not text:
            return
        
        casing_rules = self.rules.get('casing', {})
        expected = casing_rules.get(element_type, expected_case)
        
        if expected == 'title':
            # Title case: First letter of each major word capitalized
            words = text.split()
            if words and words[0][0].islower():
                self.issues.append(ValidationIssue(
                    severity='minor',
                    category='casing',
                    message=f"{element_type.title()} should use Title Case",
                    location=element_type,
                    current_text=text,
                    suggested_text=text.title()
                ))
        elif expected == 'sentence':
            # Sentence case: First letter capitalized, rest lowercase
            if text and text[0].islower():
                self.issues.append(ValidationIssue(
                    severity='minor',
                    category='casing',
                    message=f"{element_type.title()} should use sentence case",
                    location=element_type,
                    current_text=text,
                    suggested_text=text[0].upper() + text[1:]
                ))
    
    def _check_grammar_patterns(self, text: str):
        """Check common grammar mistakes."""
        patterns = [
            (r'\bthere is\s+\w+s\b', 'there is', 'there are', 'Subject-verb agreement'),
            (r'\bthere are\s+\w+[^s\s]\b', 'there are', 'there is', 'Subject-verb agreement'),
            (r'\bits\s+\w+ing\b', 'its', "it's", 'Contraction vs possessive'),
            (r'\bit\'s\s+\w+[^ing]\b', "it's", 'its', 'Contraction vs possessive'),
        ]
        
        for pattern, current, suggested, message in patterns:
            if re.search(pattern, text.lower()):
                self.issues.append(ValidationIssue(
                    severity='major',
                    category='grammar',
                    message=message,
                    location='body text',
                    current_text=f"...{current}...",
                    suggested_text=suggested
                ))


def format_report(issues: List[ValidationIssue], url: str) -> str:
    """Format validation results as readable report."""
    lines = [
        "UI Content Validation Report",
        "=" * 50,
        f"Source: {url}",
        ""
    ]
    
    if not issues:
        lines.append("✅ No issues found! Content looks good.")
        return "\n".join(lines)
    
    # Summary
    critical = len([i for i in issues if i.severity == 'critical'])
    major = len([i for i in issues if i.severity == 'major'])
    minor = len([i for i in issues if i.severity == 'minor'])
    
    lines.extend([
        f"Summary: {len(issues)} issues found",
        f"  🔴 Critical: {critical}",
        f"  🟡 Major: {major}",
        f"  🟢 Minor: {minor}",
        ""
    ])
    
    # Group by severity
    for severity in ['critical', 'major', 'minor']:
        severity_issues = [i for i in issues if i.severity == severity]
        if severity_issues:
            lines.append(f"{severity.upper()} ISSUES:")
            lines.append("-" * 40)
            
            for issue in severity_issues:
                emoji = "🔴" if severity == 'critical' else "🟡" if severity == 'major' else "🟢"
                lines.extend([
                    f"{emoji} [{issue.category.upper()}] {issue.message}",
                    f"   Location: {issue.location}",
                    f"   Current:  \"{issue.current_text[:60]}...\"",
                    f"   Suggest:  \"{issue.suggested_text[:60]}...\"",
                    ""
                ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='Validate UI content')
    parser.add_argument('--url', help='Web page URL to validate')
    parser.add_argument('--screenshot', help='Screenshot image path')
    parser.add_argument('--glossary', default='glossary.json', help='Glossary JSON file')
    parser.add_argument('--rules', default='rules.json', help='Rules JSON file')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    if not args.url and not args.screenshot:
        print("Error: Provide --url or --screenshot")
        sys.exit(1)
    
    # Load configuration
    try:
        with open(args.glossary, 'r') as f:
            glossary = json.load(f)
    except FileNotFoundError:
        glossary = {'preferred_terms': {}, 'format_rules': {}, 'casing': {}}
    
    try:
        with open(args.rules, 'r') as f:
            rules = json.load(f)
    except FileNotFoundError:
        rules = {}
    
    # Extract content
    extractor = ContentExtractor()
    if args.url:
        content = extractor.from_url(args.url)
        source = args.url
    else:
        content = extractor.from_screenshot(args.screenshot)
        source = args.screenshot
    
    # Validate
    validator = ContentValidator(glossary, rules)
    issues = validator.validate(content)
    
    # Output
    if args.json:
        result = {
            'source': source,
            'total_issues': len(issues),
            'issues': [asdict(i) for i in issues]
        }
        output = json.dumps(result, indent=2)
    else:
        output = format_report(issues, source)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
    else:
        print(output)


if __name__ == '__main__':
    main()
