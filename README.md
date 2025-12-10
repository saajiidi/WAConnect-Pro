# WAConnect Pro

WAConnect Pro is a Flask-based web application that allows users to upload Excel or CSV files (or provide a Google Sheets URL) containing contact information. It automatically identifies phone number columns, normalizes them, and generates direct WhatsApp messaging links with pre-filled messages.

## Features

- **File Support**: Upload `.xlsx`, `.xls`, or `.csv` files.
- **URL Support**: Directly process data from Google Sheets URLs.
- **Auto-Detection**: Automatically detects phone, name, and email columns.
- **Normalization**: Formats phone numbers to the E.164 standard (e.g., handles Bangladesh `01...` -> `+8801...`).
- **Template Messages**: Add a custom message to be pre-filled in the WhatsApp link.
- **Export**: detailed Excel report with clickable WhatsApp links.

## Project Structure

- `app.py`: Main Flask application handling routes and file uploads.
- `whatsapp_generator.py`: Core logic for data processing, normalization, and link generation.
- `templates/`: HTML templates for the frontend.
- `vercel.json`: Configuration for deployment on Vercel.

## Local Development

1.  **Clone the repository** (if applicable).
2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the application**:
    ```bash
    python app.py
    ```
5.  **Access the app**:
    Open your browser and navigate to `http://localhost:5000`.

## Deployment on Vercel

This project is configured for deployment on Vercel using the Python runtime.

1.  Push your code to a Git repository (GitHub, GitLab, or Bitbucket).
2.  Import the project in Vercel.
3.  Vercel should automatically detect the configuration from `vercel.json`.
4.  Deploy!

### Environment Variables
For production deployment, you should set the following environment variables in your Vercel project settings:

- `SECRET_KEY`: A random string used for session security (required for flash messages to work reliably across serverless function invocations). 
  - You can generate one using python: `python -c 'import secrets; print(secrets.token_hex(16))'`

### Note on Vercel
The application uses the `/tmp` directory for temporary file storage during processing, as Vercel's file system is read-only. This ensures compatibility with the serverless environment.
