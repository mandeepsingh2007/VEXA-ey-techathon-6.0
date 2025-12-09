from typing import List, Dict, Optional
import math


class UEBAAgent:
    """
    Very simple UEBA/security layer:
    - logs agent actions
    - computes basic anomaly score based on action frequency
    """

    def __init__(self):
        self.events: List[Dict] = []

    def log(self, actor: str, action: str, meta: Optional[Dict] = None):
        self.events.append(
            {
                "actor": actor,
                "action": action,
                "meta": meta or {},
            }
        )

    def reset(self):
        """
        Clears events to reset security status to normal.
        """
        self.events = []

    def simulate_attack(self, actor: str = "unknown_ip_89.0.1.2"):
        """
        Injects a burst of unauthorized events to trigger anomaly detection.
        """
        # Clear previous for clean demo
        self.events = []
        
        # Add normal events (more background noise for better statistics)
        # 5 normal users doing 20 events each
        for i in range(5):
             for _ in range(20):
                self.log(f"authorized_user_{i}", "login", {"status": "success"})
            
        # Add BURST of anomalous events (single bad actor doing high volume)
        for _ in range(60):
            self.log(actor, "unauthorized_access", {"status": "failed", "reason": "bad_token"})
            
    def detect_anomalies(self) -> List[Dict]:
        """
        Toy anomaly detection:
        - count actions per actor
        - flag any actor whose count > mean + 2*std
        """
        if not self.events:
            return []

        counts: Dict[str, int] = {}
        for e in self.events:
            counts[e["actor"]] = counts.get(e["actor"], 0) + 1

        values = list(counts.values())
        if not values:
            return []
            
        mean = sum(values) / len(values)
        var = sum((v - mean) ** 2 for v in values) / len(values)
        std = math.sqrt(var)

        # Lower threshold slightly for demo reliability (1.5 std dev)
        threshold = mean + max(1.5 * std, 5) 
        
        anomalies = [
            {"actor": a, "count": c, "threshold": threshold, "type": "UNAUTHORIZED_BURST"}
            for a, c in counts.items()
            if c > threshold
        ]
        return anomalies

    def report(self) -> Dict:
        return {
            "events": self.events,
            "anomalies": self.detect_anomalies(),
        }
