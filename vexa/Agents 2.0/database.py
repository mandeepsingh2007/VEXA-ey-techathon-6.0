# database.py

import sqlite3
import json
import threading
from typing import Any, Dict, List, Optional


class DatabaseManager:
    """
    Very small SQLite helper for the MagicDev prototype.

    Tables:
      - vehicles
      - health_history
      - bookings
      - recurring_defects
      - vehicle_ueba_anomalies   (NEW)
      - driver_ueba_anomalies    (NEW)
    """

    def __init__(self, db_path: str = "magicdev.db") -> None:
        # check_same_thread=False so we can safely call from threads/async wrappers
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        self.create_tables()

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------
    def create_tables(self) -> None:
        with self._lock:
            cur = self.conn.cursor()

        # Vehicles (very minimal for now)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS vehicles (
                vehicle_id TEXT PRIMARY KEY,
                owner_email TEXT,
                owner_phone TEXT,
                vehicle_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Health history – store full health summary JSON + urgency
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS health_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id TEXT,
                health_summary JSON,
                urgency TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
            )
            """
        )

        # Bookings – appointment info (Nylas or mocked)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id TEXT PRIMARY KEY,
                vehicle_id TEXT,
                appointment_time TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
            )
            """
        )

        # Recurring defects – simple counter per vehicle + component
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS recurring_defects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id TEXT,
                component TEXT,
                failure_count INTEGER,
                last_failure TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                warranty_claimed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
            )
            """
        )

        # NEW: UEBA – vehicle behaviour / health anomalies
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS vehicle_ueba_anomalies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id TEXT,
                anomaly_type TEXT,
                severity REAL,
                risk_level TEXT,
                context TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
            )
            """
        )

        # NEW: UEBA – driver anomalies (safety / behaviour)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS driver_ueba_anomalies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_id TEXT,
                anomaly_type TEXT,
                severity REAL,
                risk_level TEXT,
                context TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        self.conn.commit()

    # ------------------------------------------------------------------
    # Health + bookings
    # ------------------------------------------------------------------
    def log_health(self, vehicle_id: str, health_summary: Dict[str, Any], urgency: str) -> None:
        with self._lock:
            self.conn.execute(
                """
                INSERT INTO health_history (vehicle_id, health_summary, urgency)
                VALUES (?, ?, ?)
                """,
                (vehicle_id, json.dumps(health_summary), urgency),
            )
            self.conn.commit()

    def log_booking(self, booking_id: str, vehicle_id: str, appointment_time: str, status: str) -> None:
        with self._lock:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO bookings (booking_id, vehicle_id, appointment_time, status)
                VALUES (?, ?, ?, ?)
                """,
                (booking_id, vehicle_id, appointment_time, status),
            )
            self.conn.commit()

    def record_defect(self, vehicle_id: str, component: str) -> None:
        with self._lock:
            cur = self.conn.cursor()
        existing = cur.execute(
            """
            SELECT failure_count
            FROM recurring_defects
            WHERE vehicle_id = ? AND component = ?
            """,
            (vehicle_id, component),
        ).fetchone()

        if existing:
            cur.execute(
                """
                UPDATE recurring_defects
                SET failure_count = failure_count + 1,
                    last_failure = CURRENT_TIMESTAMP
                WHERE vehicle_id = ? AND component = ?
                """,
                (vehicle_id, component),
            )
        else:
            cur.execute(
                """
                INSERT INTO recurring_defects (vehicle_id, component, failure_count)
                VALUES (?, ?, 1)
                """,
                (vehicle_id, component),
            )
        self.conn.commit()

    # ------------------------------------------------------------------
    # NEW: UEBA anomaly logging
    # ------------------------------------------------------------------
    def log_vehicle_anomalies(self, vehicle_id: str, anomalies: List[Dict[str, Any]]) -> None:
        """
        Store UEBA anomalies for a vehicle into SQLite.

        Each anomaly dict is expected to have:
          - type
          - severity
          - risk_level
          - context
        """
        if not anomalies:
            return

        with self._lock:
            cur = self.conn.cursor()
            for a in anomalies:
                cur.execute(
                    """
                    INSERT INTO vehicle_ueba_anomalies
                    (vehicle_id, anomaly_type, severity, risk_level, context)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        vehicle_id,
                        a.get("type"),
                        float(a.get("severity", 0)),
                        a.get("risk_level", "LOW"),
                        a.get("context", ""),
                    ),
                )
            self.conn.commit()

    def log_driver_anomalies(self, driver_id: str, anomalies: List[Dict[str, Any]]) -> None:
        """
        Store UEBA anomalies for a driver into SQLite.

        Each anomaly dict is expected to have:
          - type
          - severity
          - risk_level
          - context
        """
        if not anomalies:
            return

        with self._lock:
            cur = self.conn.cursor()
            for a in anomalies:
                cur.execute(
                    """
                    INSERT INTO driver_ueba_anomalies
                    (driver_id, anomaly_type, severity, risk_level, context)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        driver_id,
                        a.get("type"),
                        float(a.get("severity", 0)),
                        a.get("risk_level", "LOW"),
                        a.get("context", ""),
                    ),
                )
            self.conn.commit()

    # Simple readers if you want to show in demo
    def get_recent_vehicle_anomalies(self, vehicle_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        cur = self.conn.cursor()
        rows = cur.execute(
            """
            SELECT *
            FROM vehicle_ueba_anomalies
            WHERE vehicle_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (vehicle_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_recent_driver_anomalies(self, driver_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        cur = self.conn.cursor()
        rows = cur.execute(
            """
            SELECT *
            FROM driver_ueba_anomalies
            WHERE driver_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (driver_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]
