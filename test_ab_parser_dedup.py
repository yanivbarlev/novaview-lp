"""
Test script to verify IP deduplication in A/B test log parser
"""

from ab_testing.ab_log_parser import ABLogParser

# Sample log data with returning users
test_logs = [
    # User 1 (IP: 192.168.1.1) - visits variant A three times
    '2025-12-11 10:00:00 INFO LANDING_PAGE keyword="test" gclid="" variant="a" ip="192.168.1.1"',
    '2025-12-11 11:00:00 INFO LANDING_PAGE keyword="test" gclid="" variant="a" ip="192.168.1.1"',
    '2025-12-11 12:00:00 INFO LANDING_PAGE keyword="test" gclid="" variant="a" ip="192.168.1.1"',

    # User 2 (IP: 192.168.1.2) - visits variant A once
    '2025-12-11 10:00:00 INFO LANDING_PAGE keyword="test" gclid="" variant="a" ip="192.168.1.2"',

    # User 3 (IP: 192.168.1.3) - visits variant B twice
    '2025-12-11 10:00:00 INFO LANDING_PAGE keyword="test" gclid="" variant="b" ip="192.168.1.3"',
    '2025-12-11 11:00:00 INFO LANDING_PAGE keyword="test" gclid="" variant="b" ip="192.168.1.3"',

    # User 4 (IP: 192.168.1.4) - visits variant B once
    '2025-12-11 10:00:00 INFO LANDING_PAGE keyword="test" gclid="" variant="b" ip="192.168.1.4"',
]

# Parse logs
parser = ABLogParser()
metrics = parser.parse_logs(test_logs)

# Calculate results
results = parser.calculate_conversion_rates()

print("=" * 60)
print("A/B Test Log Parser - IP Deduplication Test")
print("=" * 60)
print("\nTest Scenario:")
print("- Total log lines: 7")
print("- User 1 (variant A): 3 visits (same IP)")
print("- User 2 (variant A): 1 visit")
print("- User 3 (variant B): 2 visits (same IP)")
print("- User 4 (variant B): 1 visit")
print("\nExpected Results:")
print("- Variant A: 2 unique impressions (User 1 + User 2)")
print("- Variant B: 2 unique impressions (User 3 + User 4)")
print("- Ratio: 50/50 (1:1)")

print("\n" + "=" * 60)
print("Actual Results:")
print("=" * 60)
print(f"\nVariant A:")
print(f"  Unique IPs: {len(parser.unique_ips['a'])}")
print(f"  Impressions: {results['a']['impressions']}")
print(f"  Unique IPs list: {sorted(parser.unique_ips['a'])}")

print(f"\nVariant B:")
print(f"  Unique IPs: {len(parser.unique_ips['b'])}")
print(f"  Impressions: {results['b']['impressions']}")
print(f"  Unique IPs list: {sorted(parser.unique_ips['b'])}")

print(f"\nRatio A:B = {results['a']['impressions']}:{results['b']['impressions']}")

# Verify
if results['a']['impressions'] == 2 and results['b']['impressions'] == 2:
    print("\n✅ TEST PASSED: IP deduplication working correctly!")
else:
    print(f"\n❌ TEST FAILED: Expected 2:2, got {results['a']['impressions']}:{results['b']['impressions']}")

print("\n" + "=" * 60)
