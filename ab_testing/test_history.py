"""
A/B Test History Manager
Stores and retrieves completed A/B test results
"""

import json
import os
from datetime import datetime
from pathlib import Path


class TestHistoryManager:
    """Manages A/B test history and archiving"""

    def __init__(self, history_dir: str = None):
        if history_dir is None:
            _current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.history_dir = os.path.join(_current_dir, 'ab_testing', 'test_history')
        else:
            self.history_dir = history_dir

        # Create directory if it doesn't exist
        Path(self.history_dir).mkdir(parents=True, exist_ok=True)
        self.history_file = os.path.join(self.history_dir, 'test_results.json')

    def save_test_result(self, test_name: str, metrics: dict) -> bool:
        """Save test result to history"""
        try:
            # Load existing history
            history = self._load_history()

            # Create test result entry
            test_entry = {
                'name': test_name,
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics
            }

            # Add to history
            history.append(test_entry)

            # Save updated history
            self._save_history(history)
            return True
        except Exception as e:
            print(f"Error saving test result: {e}")
            return False

    def get_history(self) -> list:
        """Get all test results from history"""
        try:
            return self._load_history()
        except Exception as e:
            print(f"Error loading test history: {e}")
            return []

    def get_latest_test(self) -> dict or None:
        """Get the most recent test"""
        history = self.get_history()
        return history[-1] if history else None

    def delete_oldest_test(self) -> bool:
        """Remove oldest test from history"""
        try:
            history = self._load_history()
            if history:
                history.pop(0)
                self._save_history(history)
                return True
            return False
        except Exception as e:
            print(f"Error deleting test: {e}")
            return False

    def clear_history(self) -> bool:
        """Clear all history"""
        try:
            self._save_history([])
            return True
        except Exception as e:
            print(f"Error clearing history: {e}")
            return False

    def _load_history(self) -> list:
        """Load history from file"""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_history(self, history: list):
        """Save history to file"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
