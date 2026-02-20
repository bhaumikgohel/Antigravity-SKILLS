#!/usr/bin/env python3
"""
Smoke Test Runner
Executes automated smoke tests after deployment.
"""

import argparse
import json
import os
import sys
import time
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin


@dataclass
class TestResult:
    scenario_id: str
    scenario_name: str
    status: str  # pass, fail, skip
    duration_ms: int
    steps: List[Dict]
    screenshot_paths: List[str]
    error_message: Optional[str] = None


class SmokeTestRunner:
    """Main test execution engine."""
    
    def __init__(self, config_path: str, env: str = None):
        self.config = self._load_config(config_path, env)
        self.results: List[TestResult] = []
        self.start_time = None
        self.report_dir = None
        self.browser = None
        self.page = None
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('smoke-test')
    
    def _load_config(self, path: str, env: str) -> Dict:
        """Load and interpolate config file."""
        with open(path, 'r') as f:
            config = json.load(f)
        
        # Substitute environment variables
        config_str = json.dumps(config)
        config_str = os.path.expandvars(config_str)
        config = json.loads(config_str)
        
        # Override environment if specified
        if env:
            config['environment'] = env
        
        return config
    
    def _init_browser(self):
        """Initialize Playwright browser."""
        try:
            from playwright.sync_api import sync_playwright
            
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=True)
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            self.page = self.context.new_page()
            
            # Set default timeout
            timeout = self.config.get('timeouts', {}).get('navigation', 10000)
            self.page.set_default_timeout(timeout)
            
            self.logger.info("Browser initialized")
        except ImportError:
            raise ImportError("Install playwright: pip install playwright")
    
    def _close_browser(self):
        """Clean up browser resources."""
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
        self.logger.info("Browser closed")
    
    def _create_report_dir(self) -> Path:
        """Create timestamped report directory."""
        timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
        env = self.config.get('environment', 'unknown')
        report_dir = Path(f"./reports/smoke-{env}-{timestamp}")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # Create screenshots subdir
        (report_dir / 'screenshots').mkdir(exist_ok=True)
        
        self.logger.info(f"Report directory: {report_dir}")
        return report_dir
    
    def _take_screenshot(self, name: str) -> str:
        """Capture screenshot and return path."""
        screenshot_dir = self.report_dir / 'screenshots'
        path = screenshot_dir / f"{name}.png"
        self.page.screenshot(path=str(path), full_page=True)
        self.logger.info(f"Screenshot: {path}")
        return str(path)
    
    def _execute_step(self, step: Dict) -> Dict:
        """Execute a single test step."""
        action = step.get('action')
        step_result = {
            'action': action,
            'status': 'pass',
            'duration_ms': 0,
            'message': ''
        }
        
        start = time.time()
        
        try:
            if action == 'navigate':
                url = urljoin(self.config['base_url'], step['url'])
                self.page.goto(url)
                step_result['message'] = f"Navigated to {url}"
            
            elif action == 'click':
                self.page.click(step['selector'])
                step_result['message'] = f"Clicked {step['selector']}"
            
            elif action == 'fill':
                self.page.fill(step['selector'], step['value'])
                step_result['message'] = f"Filled {step['selector']}"
            
            elif action == 'screenshot':
                path = self._take_screenshot(step['name'])
                step_result['message'] = f"Screenshot saved: {path}"
                step_result['screenshot'] = path
            
            elif action == 'wait':
                duration = step.get('duration', 1000)
                time.sleep(duration / 1000)
                step_result['message'] = f"Waited {duration}ms"
            
            elif action == 'assert':
                selector = step['selector']
                expect = step.get('expect', 'visible')
                
                if expect == 'visible':
                    self.page.wait_for_selector(selector, state='visible')
                    step_result['message'] = f"{selector} is visible"
                elif expect == 'hidden':
                    self.page.wait_for_selector(selector, state='hidden')
                    step_result['message'] = f"{selector} is hidden"
                elif expect == 'text':
                    text = step.get('text', '')
                    element = self.page.locator(selector)
                    assert text in element.inner_text()
                    step_result['message'] = f"{selector} contains '{text}'"
            
            else:
                step_result['status'] = 'skip'
                step_result['message'] = f"Unknown action: {action}"
        
        except Exception as e:
            step_result['status'] = 'fail'
            step_result['message'] = str(e)
            # Capture error screenshot
            error_path = self._take_screenshot(f"error_{action}_{int(time.time())}")
            step_result['screenshot'] = error_path
        
        step_result['duration_ms'] = int((time.time() - start) * 1000)
        return step_result
    
    def _run_scenario(self, scenario: Dict) -> TestResult:
        """Execute a test scenario."""
        scenario_id = scenario['id']
        scenario_name = scenario['name']
        steps_config = scenario['steps']
        
        self.logger.info(f"Running scenario: {scenario_name}")
        
        steps_results = []
        screenshots = []
        overall_status = 'pass'
        error_msg = None
        
        start_time = time.time()
        
        for step in steps_config:
            result = self._execute_step(step)
            steps_results.append(result)
            
            if 'screenshot' in result:
                screenshots.append(result['screenshot'])
            
            if result['status'] == 'fail':
                overall_status = 'fail'
                error_msg = result['message']
                break
        
        duration = int((time.time() - start_time) * 1000)
        
        return TestResult(
            scenario_id=scenario_id,
            scenario_name=scenario_name,
            status=overall_status,
            duration_ms=duration,
            steps=steps_results,
            screenshot_paths=screenshots,
            error_message=error_msg
        )
    
    def run(self, scenario_filter: str = None) -> Dict:
        """Run all or filtered smoke tests."""
        self.start_time = datetime.now()
        self.report_dir = self._create_report_dir()
        
        # Initialize browser
        self._init_browser()
        
        try:
            scenarios = self.config.get('scenarios', [])
            
            # Filter if specified
            if scenario_filter:
                scenarios = [s for s in scenarios if s['id'] == scenario_filter]
            
            # Run each scenario
            for scenario in scenarios:
                result = self._run_scenario(scenario)
                self.results.append(result)
            
        finally:
            self._close_browser()
        
        return self._generate_report()
    
    def _generate_report(self) -> Dict:
        """Generate and save test report."""
        total = len(self.results)
        passed = len([r for r in self.results if r.status == 'pass'])
        failed = len([r for r in self.results if r.status == 'fail'])
        skipped = len([r for r in self.results if r.status == 'skip'])
        
        total_duration = sum(r.duration_ms for r in self.results)
        overall_status = 'PASS' if failed == 0 else 'FAIL'
        
        report = {
            'summary': {
                'timestamp': self.start_time.isoformat(),
                'environment': self.config.get('environment', 'unknown'),
                'base_url': self.config.get('base_url', ''),
                'total_scenarios': total,
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'total_duration_ms': total_duration,
                'overall_status': overall_status
            },
            'results': [asdict(r) for r in self.results]
        }
        
        # Save JSON report
        report_path = self.report_dir / 'report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate markdown report
        md_report = self._format_markdown_report(report)
        md_path = self.report_dir / 'report.md'
        with open(md_path, 'w') as f:
            f.write(md_report)
        
        self.logger.info(f"Reports saved to {self.report_dir}")
        return report
    
    def _format_markdown_report(self, report: Dict) -> str:
        """Format report as markdown."""
        summary = report['summary']
        
        lines = [
            "# Smoke Test Report",
            "",
            f"**Environment:** {summary['environment']}",
            f"**Timestamp:** {summary['timestamp']}",
            f"**Base URL:** {summary['base_url']}",
            "",
            "## Summary",
            "",
            f"- **Overall Status:** {'✅ PASS' if summary['overall_status'] == 'PASS' else '❌ FAIL'}",
            f"- **Total Scenarios:** {summary['total_scenarios']}",
            f"- **Passed:** {summary['passed']} ✅",
            f"- **Failed:** {summary['failed']} ❌",
            f"- **Skipped:** {summary['skipped']} ⏭️",
            f"- **Total Duration:** {summary['total_duration_ms'] / 1000:.1f}s",
            "",
            "## Scenario Results",
            "",
        ]
        
        for result in report['results']:
            status_icon = '✅' if result['status'] == 'pass' else '❌' if result['status'] == 'fail' else '⏭️'
            lines.extend([
                f"### {status_icon} {result['scenario_name']}",
                "",
                f"- **Status:** {result['status'].upper()}",
                f"- **Duration:** {result['duration_ms'] / 1000:.1f}s",
                "",
                "**Steps:**",
                "",
                "| Step | Action | Status | Message |",
                "|------|--------|--------|---------|"
            ])
            
            for i, step in enumerate(result['steps'], 1):
                icon = '✅' if step['status'] == 'pass' else '❌' if step['status'] == 'fail' else '⏭️'
                lines.append(f"| {i} | {step['action']} | {icon} | {step['message'][:50]}... |")
            
            lines.append("")
            
            if result['error_message']:
                lines.extend([
                    f"**Error:** {result['error_message']}",
                    ""
                ])
            
            if result['screenshot_paths']:
                lines.extend([
                    "**Screenshots:**",
                    ""
                ])
                for path in result['screenshot_paths']:
                    lines.append(f"- `{path}`")
                lines.append("")
        
        lines.extend([
            "---",
            "",
            "*Generated by Smoke Test Validation Agent*"
        ])
        
        return '\n'.join(lines)


def send_slack_notification(report: Dict, webhook_url: str, channel: str = None):
    """Send test results to Slack."""
    import requests
    
    summary = report['summary']
    color = 'good' if summary['overall_status'] == 'PASS' else 'danger'
    icon = '✅' if summary['overall_status'] == 'PASS' else '❌'
    
    # Build failed scenarios text
    failed_scenarios = [
        r['scenario_name'] 
        for r in report['results'] 
        if r['status'] == 'fail'
    ]
    
    attachment = {
        'color': color,
        'title': f"{icon} Smoke Tests {summary['overall_status']} - {summary['environment'].upper()}",
        'fields': [
            {'title': 'Environment', 'value': summary['environment'], 'short': True},
            {'title': 'Results', 'value': f"{summary['passed']}/{summary['total_scenarios']} passed", 'short': True},
            {'title': 'Duration', 'value': f"{summary['total_duration_ms'] / 1000:.1f}s", 'short': True},
        ]
    }
    
    if failed_scenarios:
        attachment['fields'].append({
            'title': 'Failed Scenarios',
            'value': '\n'.join(f"• {s}" for s in failed_scenarios),
            'short': False
        })
    
    payload = {
        'username': 'SmokeTestBot',
        'icon_emoji': ':robot_face:',
        'attachments': [attachment]
    }
    
    if channel:
        payload['channel'] = channel
    
    response = requests.post(webhook_url, json=payload)
    response.raise_for_status()
    print(f"Slack notification sent to {channel or 'default channel'}")


def main():
    parser = argparse.ArgumentParser(description='Run smoke tests')
    parser.add_argument('--config', required=True, help='Path to smoke test config JSON')
    parser.add_argument('--env', help='Environment override')
    parser.add_argument('--scenario', help='Run specific scenario only')
    parser.add_argument('--output', default='./reports', help='Output directory')
    parser.add_argument('--slack-webhook', help='Slack webhook URL')
    parser.add_argument('--channel', help='Slack channel')
    parser.add_argument('--headless', action='store_true', default=True, help='Run in headless mode')
    
    args = parser.parse_args()
    
    # Run tests
    runner = SmokeTestRunner(args.config, args.env)
    report = runner.run(args.scenario)
    
    # Print summary
    summary = report['summary']
    print(f"\n{'='*50}")
    print(f"Smoke Tests: {summary['overall_status']}")
    print(f"Passed: {summary['passed']}/{summary['total_scenarios']}")
    print(f"Failed: {summary['failed']}")
    print(f"Duration: {summary['total_duration_ms'] / 1000:.1f}s")
    print(f"{'='*50}\n")
    
    # Send Slack notification if configured
    if args.slack_webhook:
        send_slack_notification(report, args.slack_webhook, args.channel)
    
    # Exit with error code if tests failed
    sys.exit(0 if summary['overall_status'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
