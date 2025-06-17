import os
import smtplib
from email.message import EmailMessage
from typing import Any, List
from datetime import datetime

from scraper.storage.sheet_constants import DIFFERENCE_HEADERS as HEADERS


def send_diff_email(
    html_file: str = "diff.html",
    subject: str = "Diff Report",
) -> None:
    """
    Send the given HTML file as the body of an email.
    Expects these env vars to be defined:
      SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, EMAIL_FROM, EMAIL_TO
    """
    # Load file
    with open(html_file, encoding="utf-8") as f:
        html_body = f.read()

    # Build message
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.getenv("EMAIL_FROM")
    msg["To"] = os.getenv("EMAIL_TO").split(",")

    # HTML alternative
    msg.add_alternative(html_body, subtype="html")

    # Send
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", 465))
    user = os.getenv("SMTP_USER")
    pwd = os.getenv("SMTP_PASS")

    with smtplib.SMTP_SSL(host, port) as smtp:
        smtp.login(user, pwd)
        smtp.send_message(msg)


def prepare_email_body(
    records: List[List[Any]], output_file: str = "diff.html"
) -> None:
    """
    Generate an HTML report of diff records and write it to `output_file`.
    """
    # Build the inner HTML for either a “no changes” message or a table
    if not records:
        body = "<p><em>No differences detected today.</em></p>"
    else:
        # Header row
        header_row = "".join(f"<th>{col}</th>" for col in HEADERS)
        # Data rows
        data_rows = ""
        for row in records:
            cells = "".join(f"<td>{cell}</td>" for cell in row)
            data_rows += f"<tr>{cells}</tr>\n"
        body = f"""
        <table>
          <thead><tr>{header_row}</tr></thead>
          <tbody>
            {data_rows}
          </tbody>
        </table>
        """

    # Full HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Diff Report</title>
  <style>
    body {{ font-family: sans-serif; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 6px; }}
    th {{ background: #f2f2f2; text-align: left; }}
  </style>
</head>
<body>
  <h2>Diff Report — {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</h2>
  {body}
</body>
</html>"""

    # Write out the file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
