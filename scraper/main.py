#!/usr/bin/env python3
import sys
import logging

from scraper.mailer import prepare_email_body, send_diff_email
from scraper.sites.site_fetcher import get_site_records
from scraper.storage.sheets_reader import get_product_records
from scraper.comparator import (
    get_product_changes,
    get_rows_to_delete,
    normalize_site_records,
    normalize_sheet_records,
)
from scraper.storage.sheets_writer import (
    bulk_append_differences,
    bulk_append_products,
    bulk_delete_products,
    bulk_update_products,
    set_execution_date,
)

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

    # Fetch raw records from all sites
    raw_site_records = get_site_records()

    #For site fetcher test
    #print(raw_site_records)
    #return

    # Lazily‐initialized the sheet records
    raw_sheet_records = get_product_records()

    # Normalize them into a common format
    site_records = normalize_site_records(raw_site_records)
    sheet_records = normalize_sheet_records(raw_sheet_records)

    # Initialize the boolean for deletion
    is_delete = False

    # Compare the records and get the differences
    append_records, update_records, diff_records, is_delete = get_product_changes(
        site_records=site_records,
        sheet_records=sheet_records,
    )

    # Flush them all in bulk
    if update_records:
        bulk_update_products(update_records)

    if append_records:
        bulk_append_products(append_records)

    if diff_records:
        bulk_append_differences(diff_records)

    # Get modified sheet records again if is_delete is True
    if is_delete:

        raw_sheet_records = get_product_records()
        sheet_records = normalize_sheet_records(raw_sheet_records)

        del_records = get_rows_to_delete(
            site_records=site_records,
            sheet_records=sheet_records,
        )

        bulk_delete_products(del_records)

    if diff_records:
        prepare_email_body(diff_records)

        send_diff_email(
            html_file="diff.html",
            subject="🚨 Diff Report: changes detected",
        )

    # Set the execution date in the last run worksheet
    set_execution_date()


if __name__ == "__main__":
    main()
