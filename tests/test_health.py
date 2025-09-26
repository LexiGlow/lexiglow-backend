import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from wsgi import app

def test_health():
    print('=== ROUTES ===')
    for rule in app.url_map.iter_rules():
        print(rule)
    # client = app.test_client()
    # res = client.get("/health")
    # assert res.status_code == 200
    # assert res.json == {"status": "ok"}
