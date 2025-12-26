from datetime import datetime
import os
from fpdf import FPDF
import resend
from src.config.config_manager import ConfigManager

class Notifier:
    """
    Handles notifications: Console Logs, PDF Reports, and Email via Resend.
    """

    def __init__(self, config_manager, sheet_manager=None):
        self.config = config_manager
        self.sheet_manager = sheet_manager
        if self.config.resend_api_key:
            resend.api_key = self.config.resend_api_key

    def send_district_report(self, state: str, district: str, city_stats: dict):
        """
        Generates a PDF report for the completed district and emails it.
        city_stats example: {"Nashik": {"Gym": 10, "Cafe": 5}, "Pune": {...}}
        """
        print(f"\n📧 Notifier: Preparing report for {district}, {state}...")

        # 1. Generate PDF
        pdf_path = self._generate_pdf_report(state, district, city_stats)

        # 2. Construct Email Body
        total_records = sum(sum(cats.values()) for cats in city_stats.values())
        html_body = f"""
        <h2>✅ Fetch Completed: {district}, {state}</h2>
        <p>The agent has finished processing all cities in <b>{district}</b>.</p>
        <ul>
            <li><b>Total New Records:</b> {total_records}</li>
            <li><b>Cities Processed:</b> {len(city_stats)}</li>
            <li><b>Timestamp:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}</li>
        </ul>
        <p>Please find the detailed statistical report attached.</p>
        <br>
        <p><i>Sent by AI Agent</i></p>
        """

        # 3. Send Email
        if self.config.resend_api_key:
            self._send_email(
                subject=f"✅ Data Fetch Complete: {district}, {state}",
                html=html_body,
                attachments=[pdf_path],
            )
        else:
            print("⚠️ Resend Key missing. Skipping Email.")

        # 4. Log Report to Sheet (Permanent Cloud Storage)
        if self.sheet_manager:
            print("📊 Logging Report Stats to Google Sheet...")
            self.sheet_manager.log_district_report(state, district, city_stats)
        else:
            print("⚠️ SheetManager not linked. Skipping Stats Log.")

    def _generate_pdf_report(self, state, district, city_stats):
        """Creates a simple PDF table."""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, txt=f"District Report: {district}, {state}", ln=1, align="C")
        pdf.ln(10)

        # Stats Table
        pdf.set_font("Arial", "B", 12)
        pdf.cell(60, 10, "City", 1)
        pdf.cell(80, 10, "Category", 1)
        pdf.cell(40, 10, "Count", 1)
        pdf.ln()

        pdf.set_font("Arial", size=12)

        for city, cats in city_stats.items():
            for cat, count in cats.items():
                pdf.cell(60, 10, city, 1)
                pdf.cell(80, 10, cat, 1)
                pdf.cell(40, 10, str(count), 1)
                pdf.ln()

        # Save
        filename = (
            f"logs/Report_{district}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        )
        os.makedirs("logs", exist_ok=True)
        pdf.output(filename)
        print(f"📄 PDF Report generated: {filename}")
        return filename

    def _send_email(self, subject, html, attachments):
        try:
            params = {
                "from": "AI Agent <support@pystack.site>",
                "to": ["sohailshaikharifshaikh07@gmail.com"],
                "subject": subject,
                "html": html,
                "attachments": [],
            }

            # Read attachment bytes
            for path in attachments:
                with open(path, "rb") as f:
                    content = f.read()

                params["attachments"].append(
                    {
                        "filename": os.path.basename(path),
                        "content": list(content),
                    }
                )

            r = resend.Emails.send(params)
            print(f"📧 Email Sent! ID: {r.get('id')}")

        except Exception as e:
            print(f"❌ Email Failed: {e}")
