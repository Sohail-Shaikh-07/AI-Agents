from app.services.sheets import (
    get_sheet_service,
    GOOGLE_SHEET_ID,
    GOOGLE_SHEET_URL,
    SHEET_NAME,
)
import gspread


def fix_headers():
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

        # Exact headers requested
        headers = [
            "Date Found",
            "Date Posted",  # Added based on your request for "real time date"
            "Source (Indeed/LinkedIn)",
            "Job Title",
            "Company",
            "Location",
            "Job Link",
            "Salary Range",
            "Job Description",
            "Status",
        ]

        # Update first row
        sheet.update("A1:J1", [headers])  # 10 columns
        print("Headers updated successfully!")
        print(headers)

    except Exception as e:
        print(f"Error updating headers: {e}")


if __name__ == "__main__":
    fix_headers()
