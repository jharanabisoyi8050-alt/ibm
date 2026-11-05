"""
DBSCAN Hotspot Detection Model
Identifies accident-prone zones by clustering historical accident coordinates.
"""
import numpy as np
import asyncio
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class HotspotDetectionModel:
    """DBSCAN-based geographic clustering for accident hotspot identification."""

    def __init__(self, eps_km: float = 0.5, min_samples: int = 3):
        self.eps_km = eps_km
        self.min_samples = min_samples

    def detect_clusters(self, accidents: list[dict]) -> list[dict]:
        """Run DBSCAN on accident coordinates and return hotspot clusters."""
        if len(accidents) < self.min_samples:
            return []

        from sklearn.cluster import DBSCAN
        coords = np.array([[a["lat"], a["lng"]] for a in accidents])
        eps_radians = self.eps_km / 6371.0  # Convert km to radians

        db = DBSCAN(
            eps=eps_radians,
            min_samples=self.min_samples,
            algorithm="ball_tree",
            metric="haversine",
        ).fit(np.radians(coords))

        clusters = {}
        for idx, label in enumerate(db.labels_):
            if label == -1:
                continue
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(accidents[idx])

        result = []
        for label, members in clusters.items():
            lats = [m["lat"] for m in members]
            lngs = [m["lng"] for m in members]
            severities = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
            max_sev = max(members, key=lambda m: severities.get(m.get("severity", "LOW"), 1))
            risk_score = min(100, len(members) * 10)
            result.append({
                "cluster_id": int(label),
                "center_lat": round(np.mean(lats), 6),
                "center_lng": round(np.mean(lngs), 6),
                "radius_m": self.eps_km * 1000,
                "incident_count": len(members),
                "risk_score": risk_score,
                "risk_level": "CRITICAL" if risk_score >= 80 else "HIGH" if risk_score >= 50 else "MEDIUM",
            })

        return sorted(result, key=lambda c: c["risk_score"], reverse=True)

    async def detect_clusters_async(self, lat: float, lng: float, radius_km: float) -> list[dict]:
        """Async wrapper - fetches accidents from DB and runs clustering."""
        # In production: query accident_reports from DB within radius
        # For now: generate synthetic accidents for demonstration
        import random
        synthetic = [
            {
                "lat": lat + random.uniform(-radius_km / 111, radius_km / 111),
                "lng": lng + random.uniform(-radius_km / 111, radius_km / 111),
                "severity": random.choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"]),
            }
            for _ in range(random.randint(20, 80))
        ]
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.detect_clusters, synthetic)
