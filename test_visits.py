"""Run: python3 test_visits.py  (uses a throwaway sqlite db, no network)"""
import os
import tempfile
from datetime import datetime, timedelta

os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(tempfile.mkdtemp(), "visits_test.db")
os.environ.setdefault("QWEN_API_KEY", "test-key")  # app.py 会初始化 LLM 客户端

from flask_jwt_extended import create_access_token  # noqa: E402

from app import app  # noqa: E402
from db.extensions import db  # noqa: E402
from db.models import Visit  # noqa: E402


def main():
    with app.app_context():
        db.create_all()
        db.session.query(Visit).delete()
        db.session.commit()

        client = app.test_client()

        assert client.post("/api/visits", json={"path": "/"}).status_code == 400

        assert client.post("/api/visits", json={"device_id": "dev-a", "path": "/"}).get_json()["recorded"] is True
        # 同设备同页面在窗口内去重
        assert client.post("/api/visits", json={"device_id": "dev-a", "path": "/"}).get_json()["recorded"] is False
        assert client.post("/api/visits", json={"device_id": "dev-a", "path": "/cart"}).get_json()["recorded"] is True
        assert client.post("/api/visits", json={"device_id": "dev-b", "path": "/"}).get_json()["recorded"] is True
        assert Visit.query.count() == 3

        # 昨天的老访问：算进总量，不算进今日
        db.session.add(Visit(device_id="dev-c", path="/", created_at=datetime.utcnow() - timedelta(days=1)))
        db.session.commit()

        token = create_access_token(identity="test-admin", additional_claims={"role": "superadmin"})
        stats = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {token}"}).get_json()["visits"]
        assert stats["total_pv"] == 4, stats
        assert stats["total_uv"] == 3, stats
        assert stats["today_pv"] == 3, stats
        assert stats["today_uv"] == 2, stats
        assert len(stats["daily_trend"]) == 7, stats
        assert sum(day["pv"] for day in stats["daily_trend"]) == 4, stats
        print("ok:", stats)


if __name__ == "__main__":
    main()
