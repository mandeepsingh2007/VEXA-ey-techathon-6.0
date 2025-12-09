from typing import Dict


class FeedbackAgent:
    """
    Simulates post-service feedback capture.
    """

    def collect_feedback(self, rating: int, comments: str = "") -> Dict:
        return {
            "rating": rating,
            "comments": comments,
            "csat_bucket": (
                "PROMOTER" if rating >= 9 else "PASSIVE" if rating >= 7 else "DETRACTOR"
            ),
        }
