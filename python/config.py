"""
Database Configuration
Configure your Oracle database connection details here.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Oracle Database Connection Settings
ORACLE_HOST = os.getenv("ORACLE_HOST", "localhost")
ORACLE_PORT = int(os.getenv("ORACLE_PORT", "1521"))
ORACLE_SID = os.getenv("ORACLE_SID", "ORCL")
ORACLE_USER = os.getenv("ORACLE_USER", "")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "")

# Connection Pool Settings
CONNECTION_POOL_MIN = 2
CONNECTION_POOL_MAX = 10
CONNECTION_POOL_INCREMENT = 2

# Logging
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Validation
if not ORACLE_USER or not ORACLE_PASSWORD:
    raise ValueError(
        "Oracle credentials not configured. "
        "Set ORACLE_USER and ORACLE_PASSWORD environment variables or in .env file"
    )