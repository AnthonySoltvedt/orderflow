
# Lesson 21: Logging Configuration

import logging
from pathlib import Path

# Create a logs folder
LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=LOG_DIR / "orderflow.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Create our logger
logger = logging.getLogger("orderflow")


# Test the logging system
if __name__ == "__main__":
    logger.info("OrderFlow logging system started.")
    logger.warning("This is a test warning.")
    logger.error("This is a test error.")

    print("Logging test complete.")
