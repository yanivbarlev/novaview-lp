"""
A/B Test Log Parser
Parses Flask application logs to extract A/B test metrics
"""

import re
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple

class ABLogParser:
    def __init__(self, log_file_path: str = None):
        self.log_file_path = log_file_path
        self.metrics = {
            'a': {'impressions': 0, 'conversions': 0, 'clicks': 0, 'exit_popup_shows': 0},
            'b': {'impressions': 0, 'conversions': 0, 'clicks': 0, 'exit_popup_shows': 0}
        }

    def parse_logs(self, lines: List[str] = None) -> Dict:
        """Parse log lines and extract A/B test metrics"""
        if lines is None:
            if self.log_file_path:
                with open(self.log_file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            else:
                return self.metrics

        for line in lines:
            # Parse LANDING_PAGE events (impressions)
            if 'LANDING_PAGE' in line:
                variant = self._extract_field(line, 'variant')
                if variant in ['a', 'b']:
                    self.metrics[variant]['impressions'] += 1

            # Parse CONVERSION events
            elif 'CONVERSION' in line:
                variant = self._extract_field(line, 'variant')
                if variant in ['a', 'b']:
                    self.metrics[variant]['conversions'] += 1

            # Parse CTA_CLICK events
            elif 'CTA_CLICK' in line:
                variant = self._extract_field(line, 'variant')
                if variant in ['a', 'b']:
                    self.metrics[variant]['clicks'] += 1

            # Parse EXIT_POPUP_EVENT (show events only)
            elif 'EXIT_POPUP_EVENT' in line and 'event="exit_popup_shown"' in line:
                variant = self._extract_field(line, 'variant')
                if variant in ['a', 'b']:
                    self.metrics[variant]['exit_popup_shows'] += 1

        return self.metrics

    def _extract_field(self, log_line: str, field_name: str) -> str:
        """Extract field value from log line"""
        pattern = f'{field_name}="([^"]*)"'
        match = re.search(pattern, log_line)
        return match.group(1) if match else ''

    def calculate_conversion_rates(self) -> Dict:
        """Calculate conversion rates for each variant"""
        results = {}

        for variant in ['a', 'b']:
            impressions = self.metrics[variant]['impressions']
            conversions = self.metrics[variant]['conversions']
            clicks = self.metrics[variant]['clicks']

            conv_rate = (conversions / impressions * 100) if impressions > 0 else 0.0
            click_rate = (clicks / impressions * 100) if impressions > 0 else 0.0

            results[variant] = {
                'impressions': impressions,
                'conversions': conversions,
                'clicks': clicks,
                'exit_popup_shows': self.metrics[variant]['exit_popup_shows'],
                'conversion_rate': round(conv_rate, 2),
                'click_rate': round(click_rate, 2)
            }

        return results

    def get_winner(self, min_impressions: int = 100) -> Tuple[str, Dict]:
        """Determine winning variant based on conversion rate"""
        results = self.calculate_conversion_rates()

        # Check if we have enough data
        if results['a']['impressions'] < min_impressions or results['b']['impressions'] < min_impressions:
            return 'insufficient_data', results

        # Compare conversion rates
        if results['a']['conversion_rate'] > results['b']['conversion_rate']:
            winner = 'a'
        elif results['b']['conversion_rate'] > results['a']['conversion_rate']:
            winner = 'b'
        else:
            winner = 'tie'

        return winner, results
