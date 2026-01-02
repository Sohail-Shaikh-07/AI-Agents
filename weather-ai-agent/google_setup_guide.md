# Google Sheets Setup Guide

To let the AI Agent write data to your Google Sheet, you need to create a "Service Account" (a robot user) and give it access.

## Step 1: Create Service Account

1.  Go to **[Google Cloud Console](https://console.cloud.google.com/)**.
2.  Create a **New Project** (e.g., "Weather Agent").
3.  Search for **"Google Sheets API"** and **Enable** it.
4.  Search for **"Google Drive API"** and **Enable** it.
5.  Go to **Credentials** -> **Create Credentials** -> **Service Account**.
6.  Give it a name (e.g., "agent-bot"). Click **Done**.
7.  Click on the new Service Account email (e.g., `agent-bot@...iam.gserviceaccount.com`).
8.  Go to **Keys** tab -> **Add Key** -> **Create new key** -> **JSON**.
9.  A file (`credential.json`) will download. **Keep this safe!**

## Step 2: Configure Environment (.env)

We use a Base64 encoded string for the credentials to easily paste them into `.env` or Render.

1.  **Encode your JSON:**

    - **Mac/Linux:** `base64 -i credential.json`
    - **Windows (PowerShell):**
      ```powershell
      [Convert]::ToBase64String([IO.File]::ReadAllBytes("path\to\credential.json"))
      ```
    - **Online Tool:** Search "Base64 Encode" (Paste JSON content).

2.  **Update `.env` file:**
    Open the `.env` file in the main project folder and add:

    ```ini
    GOOGLE_SHEET_ID=your_spreadsheet_id
    GOOGLE_JSON=paste_your_long_base64_string_here
    ```

## Step 3: Share the Sheet [CRITICAL STEP]

> [!IMPORTANT] > **If you skip this, the agent will crash with a 403 Forbidden Error.**

1.  Open your `credential.json` file (text editor).
2.  Find the `"client_email"` field.
    - It looks like: `agent-bot@your-project-id.iam.gserviceaccount.com`
3.  **Copy this email address.**
4.  Go to your target **Google Sheet** in your browser.
5.  Click the big **Share** button (top right).
6.  **Paste the Service Account Email**.
7.  **Select "Editor"** from the role dropdown.
8.  Click **Send**.

## Step 4: Get Sheet ID

The ID is in the URL of your Google Sheet:
`https://docs.google.com/spreadsheets/d/` **`1aBcD...eFgH`** `/edit`

Copy that ID into `GOOGLE_SHEET_ID` in your `.env` file.

---

**Done!** Your agent can now read/write to this sheet.
