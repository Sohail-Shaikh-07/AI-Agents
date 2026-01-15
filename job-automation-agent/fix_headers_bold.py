from app.services.sheets import (
    get_sheet_service,
    GOOGLE_SHEET_ID,
    GOOGLE_SHEET_URL,
    SHEET_NAME,
)
import gspread
from gspread_formatting import *


def fix_headers_bold():
    client = get_sheet_service()
    if not client:
        print("Could not connect to sheets service.")
        return

    try:
        if GOOGLE_SHEET_ID:
            sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1
        elif GOOGLE_SHEET_URL:
            sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        else:
            sheet = client.open(SHEET_NAME).sheet1

        print(f"Connected to sheet: {sheet.title}")

        # Headers requested
        headers = [
            "Date Found",
            "Date Posted",
            "Source (Indeed/LinkedIn)",
            "Job Title",
            "Company",
            "Location",
            "Job Link",
            "Salary Range",
            "Job Description",
            "Status",
        ]

        # 1. Insert Row at Index 1 (pushes existing data down)
        print("Inserting headers at Row 1...")
        sheet.insert_row(headers, index=1)

        # 2. Format Row 1 as Bold + Frozen
        print("Formatting headers...")
        fmt = cellFormat(textFormat=textFormat(bold=True), horizontalAlignment="CENTER")
        format_cell_range(sheet, "A1:J1", fmt)
        set_frozen(sheet, rows=1)

        print("Success! Headers inserted and bolded.")

    except Exception as e:
        print(f"Error correcting headers: {e}")


if __name__ == "__main__":
    fix_headers_bold()
