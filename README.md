# DraftSpace

A lightweight collaborative document editor built with Flask, SQLite and Quill.js.

DraftSpace allows users to create, edit, rename, upload and share documents through a simple browser-based interface.

## Live Application

https://iamdamilola.pythonanywhere.com/

## GitHub Repository

https://github.com/isadamilola/draftspace

## Features

- Create, edit and reopen documents.
- Rename documents (owner only).
- Rich-text editing with bold, italic, underline, headings, bullet lists and numbered lists.
- Automatic saving after a short delay, with manual save available.
- Upload `.txt` and `.md` files (maximum 500 KB) as editable documents.
- Share documents with other users by username.
- Separate dashboard sections for documents you own and documents shared with you.
- Persistent document storage using SQLite.
- Access control for document owners and shared users.

## Technology Stack

- **Backend:** Python, Flask
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript
- **Rich-text editor:** Quill.js
- **Testing:** Pytest
- **Deployment:** PythonAnywhere

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/isadamilola/draftspace.git
cd draftspace
```

### 2. Create a virtual environment

Python 3.12 is recommended.

On Windows:

```bash
py -3.12 -m venv venv
venv\Scripts\activate
```

On macOS/Linux:

```bash
python3.12 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the secret key

Set a Flask secret key before running the application.

On Windows PowerShell:

```powershell
$env:SECRET_KEY = "your-secret-key"
```

On macOS/Linux:

```bash
export SECRET_KEY="your-secret-key"
```

For a local development key, you can generate one with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Start the application

```bash
flask --app app run --debug
```

Open the local address shown in your terminal, usually:

`http://127.0.0.1:5000`

The application initializes its SQLite database when it starts.

## Test Accounts

DraftSpace uses mocked login for this assessment. No passwords are required.

Available accounts:

- `dami`
- `alice`
- `bob`

To test sharing:

1. Log in as `dami`.
2. Create a document.
3. Share it with `alice`.
4. Open another browser session and log in as `alice`.
5. Open the document from the **Shared with me** section.

## Running Tests

Run the automated tests with:

```bash
pytest -v
```

The included test covers document ownership, access denial for unauthorized users, and access granted to a shared user.

## Current Limitations

The following features were deliberately left outside the assessment's implementation:

- Real user authentication and password management.
- Revoking document access.
- `.docx` file uploads.
- Markdown-to-rich-text conversion during import.
- Real-time collaborative editing.
- Document version history.
- Additional automated tests for all routes and upload scenarios.

## Project Structure

```text
draftspace/
├── app.py
├── schema.sql
├── requirements.txt
├── test_app.py
├── log.md
├── README.md
├── SUBMISSION.md
└── templates/
    ├── login.html
    ├── dashboard.html
    └── editor.html
```

`app.db` is generated locally when the application runs and is not included in the repository.
