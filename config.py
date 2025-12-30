import getpass
import logging
import os
import socket
import sys
from typing import List
from urllib.parse import urlparse

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# === ENVIRONMENT-BASED LOGGING CONFIGURATION ===
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO" if ENVIRONMENT == "development" else "WARNING")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format="%(levelname)s:%(name)s:%(message)s"
)

# Reduce verbose logging in production
if ENVIRONMENT == "production":
    logging.getLogger("api.dependencies").setLevel(logging.WARNING)
    logging.getLogger("api.database").setLevel(logging.WARNING)
    logging.getLogger("api.database.connection_pool").setLevel(logging.WARNING)


def suppress_service_logging():
    """Silence routine service logs to clean scraper experience."""
    service_loggers = [
        "services.database_service",
        "services.image_processing_service",
        "services.session_manager",
        "services.connection_pool",
        "services.metrics_collector",
        "utils.secure_scraper_loader",
        "utils.config_loader",
        "utils.organization_sync_service",
        "utils.db_connection",
        "WDM",  # WebDriver Manager
        "selenium",
    ]
    for service_name in service_loggers:
        logging.getLogger(service_name).setLevel(logging.WARNING)
    logging.getLogger(__name__).setLevel(logging.WARNING)


def enable_world_class_scraper_logging():
    """Set logging levels for scraper."""
    suppress_service_logging()
    logging.getLogger("scraper").setLevel(logging.INFO)


logger = logging.getLogger(__name__)

# --- Safety Check ---
IS_TESTING = os.environ.get("TESTING") == "true"
logger.info(f"[config.py] TESTING environment variable detected: {IS_TESTING}")

# Get system username
system_user = getpass.getuser()
logger.debug(f"[config.py] System user detected: {system_user}")


def parse_database_url(url: str) -> dict:
    """Parse DATABASE_URL into components."""
    parsed = urlparse(url)
    if parsed.scheme not in ("postgresql", "postgres"):
        raise ValueError(f"Invalid database URL scheme: {parsed.scheme}")
    return {
        "host": parsed.hostname or "localhost",
        "database": parsed.path.lstrip("/") if parsed.path else "rescue_dogs",
        "user": parsed.username or system_user,
        "password": parsed.password or "",
        "port": parsed.port or 5432,
    }


def get_database_config() -> dict:
    """Get database configuration from environment (DATABASE_URL prioritized)."""
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        logger.info("[config.py] Using DATABASE_URL for database configuration")
        config = parse_database_url(database_url)
        return {
            "host": config["host"],
            "database": config["database"],
            "user": config["user"],
            "password": config["password"],
            "port": config["port"],
        }
    # Fallback to defaults
    default_db_name = "test_rescue_dogs" if IS_TESTING else "rescue_dogs"
    return {
        "host": "localhost",
        "database": default_db_name,
        "user": "test_user" if IS_TESTING else system_user,
        "password": "test_password" if IS_TESTING else "",
        "port": 5432,
    }


DB_CONFIG = get_database_config()

# --- Final Safety Check ---
final_db_name = DB_CONFIG["database"]
logger.info(f"[config.py] Final DB_CONFIG constructed with database: {final_db_name}")

if IS_TESTING and final_db_name != "test_rescue_dogs":
    logger.error(f"CRITICAL SAFETY ERROR: TESTING is true but DB_CONFIG is set to '{final_db_name}'")
    sys.exit("CRITICAL SAFETY ERROR: Test environment configured to use non-test database.")

if not IS_TESTING and final_db_name == "test_rescue_dogs":
    logger.warning(f"SAFETY WARNING: TESTING is false but DB_CONFIG is set to test database '{final_db_name}'")

# Log final DB_CONFIG (safe)
logger.debug(f"[config.py]   host: {DB_CONFIG['host']}")
logger.debug(f"[config.py]   database: {DB_CONFIG['database']}")
logger.debug(f"[config.py]   user: [REDACTED]")
logger.debug(f"[config.py]   password: {'[SET]' if DB_CONFIG['password'] else '[NOT SET]'}")


# === CORS CONFIGURATION ===
def parse_cors_origins() -> List[str]:
    """Parse ALLOWED_ORIGINS from environment variable."""
    origins_env = os.getenv("ALLOWED_ORIGINS", "")
    if not origins_env:
        if ENVIRONMENT == "development":
            default_origins = [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:3001",
            ]
            logger.warning(f"No ALLOWED_ORIGINS set in development. Using defaults: {default_origins}")
            return default_origins
        else:
            raise ValueError("ALLOWED_ORIGINS must be set in production")
    origins = [origin.strip() for origin in origins_env.split(",") if origin.strip()]
    validated_origins = []
    for origin in origins:
        if not (origin.startswith("http://") or origin.startswith("https://")):
            logger.error(f"Invalid origin format: {origin}")
            continue
        if ENVIRONMENT == "production" and origin.startswith("http://"):
            logger.warning(f"Insecure HTTP origin in production: {origin}")
        validated_origins.append(origin)
    if not validated_origins:
        raise ValueError("No valid origins found in ALLOWED_ORIGINS")
    return validated_origins


def get_local_ip():
    """Get local IP address."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "localhost"


def get_dynamic_cors_origins():
    """Get CORS origins including local network IP in development."""
    base_origins = parse_cors_origins()
    if ENVIRONMENT == "development":
        local_ip = get_local_ip()
        network_origin = f"http://{local_ip}:3000"
        if network_origin not in base_origins:
            base_origins.append(network_origin)
            logger.info(f"[config.py] Added dynamic CORS origin: {network_origin}")
    logger.info(f"[config.py] Final CORS origins: {base_origins}")
    return base_origins


ALLOWED_ORIGINS = get_dynamic_cors_origins()
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() == "true"

if ENVIRONMENT == "production":
    CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS = [
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
        "sentry-trace",
        "baggage",
    ]
    CORS_MAX_AGE = 3600
else:
    CORS_ALLOW_METHODS = ["*"]
    CORS_ALLOW_HEADERS = ["*"]
    CORS_MAX_AGE = 86400

logger.info(f"[config.py] Environment: {ENVIRONMENT}")
logger.info(f"[config.py] CORS allowed origins: {ALLOWED_ORIGINS}")
logger.info(f"[config.py] CORS credentials allowed: {CORS_ALLOW_CREDENTIALS}")
logger.info(f"[config.py] CORS methods: {CORS_ALLOW_METHODS}")
