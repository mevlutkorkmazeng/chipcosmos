"""Basit sistem telemetrisi: CPU/RAM/disk kullanımı + bilgi tabanı istatistikleri.

vectorvault-enterprise'daki 'System Telemetry' sayfasının sade bir karşılığı
(canlı grafik/log geçmişi yok, anlık bir snapshot).
"""

import time

import psutil
from fastapi import APIRouter

from config import PROJECT_DIR
from db import get_connection

router = APIRouter()

_PROCESS_START = time.time()


def _bytes_to_gb(value: int) -> float:
    return round(value / (1024 ** 3), 2)


@router.get("/telemetry")
def get_telemetry():
    cpu_percent = psutil.cpu_percent(interval=0.2)

    mem = psutil.virtual_memory()
    disk = psutil.disk_usage(str(PROJECT_DIR.anchor or "/"))

    conn = get_connection()
    doc_count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    chunk_count = conn.execute("SELECT COUNT(*) FROM vector_chunks").fetchone()[0]
    topic_rows = conn.execute(
        "SELECT topic, COUNT(*) AS doc_count, COALESCE(SUM(chunk_count), 0) AS chunks "
        "FROM documents GROUP BY topic"
    ).fetchall()
    status_rows = conn.execute(
        "SELECT status, COUNT(*) AS count FROM documents GROUP BY status"
    ).fetchall()
    conn.close()

    uptime_seconds = round(time.time() - _PROCESS_START)

    return {
        "system": {
            "cpu_percent": cpu_percent,
            "cpu_cores": psutil.cpu_count(logical=True),
            "ram": {
                "used_gb": _bytes_to_gb(mem.used),
                "total_gb": _bytes_to_gb(mem.total),
                "percent": mem.percent,
            },
            "disk": {
                "used_gb": _bytes_to_gb(disk.used),
                "total_gb": _bytes_to_gb(disk.total),
                "percent": disk.percent,
            },
        },
        "runtime": {
            "uptime_seconds": uptime_seconds,
            "offline": True,
        },
        "knowledge_base": {
            "document_count": doc_count,
            "chunk_count": chunk_count,
            "by_topic": [dict(row) for row in topic_rows],
            "by_status": [dict(row) for row in status_rows],
        },
    }
