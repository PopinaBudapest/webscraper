#!/usr/bin/env python3
import sys
import logging

from scraper.mailer import prepare_email_body, send_diff_email
from scraper.sites.site_fetcher import get_site_records
from scraper.storage.sheets_reader import get_product_records
from scraper.comparator import *
from scraper.storage.sheets_writer import *

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Configure logging for the whole app
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def main():

    logger.info("Starting the scraper...")

    # Fetch records from all sites and from Google Sheets
    site_records = get_site_records()
    sheet_records = get_product_records()

    # Compare the records and get the differences
    diff_records = get_product_changes(
        site_records=site_records,
        sheet_records=sheet_records,
    )  

    if diff_records:

        bulk_append_products(site_records)
        bulk_append_differences(diff_records)

        average_records = get_type_averages(site_records)
        bulk_replace_averages(average_records)

        prepare_email_body(diff_records)

        send_diff_email(
            html_file="diff.html",
            subject="🚨 Diff Report: changes detected",
        )

    # Set the execution date in the last run worksheet
    set_execution_date()


if __name__ == "__main__":
    main()
