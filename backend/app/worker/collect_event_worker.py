import time
import logging
from datetime import datetime

from app.services.collect_event import sync_seoul_events

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# 주기적(1일 1회회)으로 수행하는 워커.
INTERVAL_SECONDS = 60 * 60 * 24   # 24h


def collect_seoul_events_worker():
    logger.info("Seoul event worker started. Interval=%d seconds", INTERVAL_SECONDS)

    while True:
        try:
            logger.info("Starting sync job at %s", datetime.now().isoformat())
            saved = sync_seoul_events()
            logger.info("Sync job finished. newly_saved=%d", saved)
        except Exception as e:
            logger.exception("Seoul event sync failed: %s", e)

        logger.info("Sleeping for %d seconds...", INTERVAL_SECONDS)
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    collect_seoul_events_worker()
