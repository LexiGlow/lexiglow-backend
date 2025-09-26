from wsgi import connexion_app
from app.controllers.health import get_health
app = connexion_app.app
print('=== ROUTES ===')
print(get_health())
for rule in app.url_map.iter_rules():
    print(str(rule))