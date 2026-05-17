import logging
import time
from apscheduler.schedulers.background import BackgroundScheduler

from app.db import init_db
from app.publisher_service import publish_due_posts
from config.settings import CHECK_INTERVAL_SECONDS


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler("logs/scheduler.log", encoding="utf-8"),
            logging.StreamHandler()
        ],
        force=True
    )


def scheduled_job():
    count = publish_due_posts()
    logging.info("publish_due_posts finished, processed=%s", count)


def main():
    init_db()
    setup_logging()

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        scheduled_job,
        trigger="interval",
        seconds=CHECK_INTERVAL_SECONDS,
        id="publish_due_posts_job",
        max_instances=1,
    )
    scheduler.start()

    logging.info("Scheduler started with interval=%s seconds", CHECK_INTERVAL_SECONDS)

    try:
        scheduled_job()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Scheduler stopped by user")
    finally:
        scheduler.shutdown()


if __name__ == "__main__":
    main()
