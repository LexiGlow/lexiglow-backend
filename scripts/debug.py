import logging
from wsgi import connexion_app
from app.controllers.health import get_health

# Configure logging for debug script
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = connexion_app.app
logger.info("=== ROUTES ===")
logger.info(get_health())
for rule in app.url_map.iter_rules():
    logger.info(str(rule))
