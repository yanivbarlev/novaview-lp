"""
A/B Test Log Parser
Parses Flask application logs to extract A/B test metrics with statistical significance

IMPORTANT: Impressions are deduplicated by IP address to account for returning users.
This ensures accurate A/B test results by counting unique users, not total page views.
"""

import re
import math
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
        # Track unique IPs per variant to deduplicate returning users
        self.unique_ips = {
            'a': set(),
            'b': set()
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
            # Parse LANDING_PAGE and STACKFREE_PAGE events (impressions)
            if 'LANDING_PAGE' in line or 'STACKFREE_PAGE' in line:
                variant = self._extract_field(line, 'variant')
                ip = self._extract_field(line, 'ip')
                if variant in ['a', 'b'] and ip:
                    # Track unique IPs to deduplicate returning users
                    self.unique_ips[variant].add(ip)

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

        # Update impression counts from unique IPs
        for variant in ['a', 'b']:
            self.metrics[variant]['impressions'] = len(self.unique_ips[variant])

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

    def calculate_statistical_significance(self, confidence_level: float = 0.95) -> Dict:
        """
        Calculate 95% confidence interval for conversion rates using Wilson score interval
        Returns confidence intervals and p-value for each variant
        """
        results = self.calculate_conversion_rates()
        z_score = 1.96  # For 95% confidence interval

        for variant in ['a', 'b']:
            impressions = results[variant]['impressions']
            conversions = results[variant]['conversions']

            if impressions == 0:
                results[variant]['confidence_interval'] = (0, 0)
                results[variant]['margin_of_error'] = 0
                results[variant]['confidence_pct'] = 0
                continue

            # Calculate conversion rate
            p = conversions / impressions if impressions > 0 else 0

            # Wilson score interval (more accurate for small samples)
            denominator = 1 + (z_score**2) / impressions
            center = (p + (z_score**2) / (2 * impressions)) / denominator
            margin = z_score * math.sqrt((p * (1 - p) / impressions) + (z_score**2 / (4 * impressions**2))) / denominator

            lower = max(0, (center - margin) * 100)
            upper = min(100, (center + margin) * 100)

            results[variant]['confidence_interval'] = (round(lower, 2), round(upper, 2))
            results[variant]['margin_of_error'] = round(margin * 100, 2)
            results[variant]['confidence_pct'] = 95

        # Calculate p-value using two-proportion z-test
        results['p_value'] = self._calculate_p_value(
            results['a']['conversions'],
            results['a']['impressions'],
            results['b']['conversions'],
            results['b']['impressions']
        )

        # Statistical significance (p < 0.05)
        results['is_significant'] = results['p_value'] < 0.05

        return results

    def _calculate_p_value(self, conversions_a: int, impressions_a: int,
                          conversions_b: int, impressions_b: int) -> float:
        """Calculate p-value using two-proportion z-test"""
        if impressions_a == 0 or impressions_b == 0:
            return 1.0

        p_a = conversions_a / impressions_a
        p_b = conversions_b / impressions_b
        p_pool = (conversions_a + conversions_b) / (impressions_a + impressions_b)

        if p_pool == 0 or p_pool == 1:
            return 1.0

        se = math.sqrt(p_pool * (1 - p_pool) * (1 / impressions_a + 1 / impressions_b))

        if se == 0:
            return 1.0

        z_score = abs(p_a - p_b) / se

        # Two-tailed p-value
        from math import erf
        p_value = 1 - erf(z_score / math.sqrt(2)) / 2
        return round(p_value, 4)
