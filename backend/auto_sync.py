
# Lesson 21: Automatic Synchronisation with Logging

import time
from datetime import datetime

from mock_woocommerce import sync_mock_orders
from logger_config import logger


def run_scheduler():
    print("OrderFlow automatic synchronisation started.")
    logger.info("Automatic synchronisation scheduler started.")

    try:
        while True:
            print("Starting synchronisation...")
            logger.info("Synchronisation started.")

            try:

                sync_mock_orders(import_mode=True)
                logger.info("Synchronisation finished.")

            except Exception:
                logger.exception("Synchronisation failed.")
                print("Synchronisation failed. Check orderflow.log.")

            logger.info("Synchronisation finished.")
            print("Next synchronisation in 60 seconds.\n")

            time.sleep(60)

    except KeyboardInterrupt:
        print("\nOrderFlow automatic synchronisation stopped.")
        logger.info("Automatic synchronisation scheduler stopped.")


if __name__ == "__main__":
    run_scheduler()
