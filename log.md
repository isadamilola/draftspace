## Final Development Log — DraftSpace

**Date:** 14 November 2026

### Deployment

- Created a PythonAnywhere account and configured a Python 3.12 web application.
- Cloned the DraftSpace GitHub repository onto PythonAnywhere.
- Created a virtual environment named `draftenv`.
- Installed project dependencies from `requirements.txt`.
- Verified that the Flask application imports successfully on the server.
- Configured the WSGI file to load the Flask application.
- Generated a secure secret key for the deployed application.
- Connected the project directory and virtual environment to the web app.
- Successfully deployed DraftSpace at https://iamdamilola.pythonanywhere.com/.

### Live Application Testing

- Confirmed that the deployed application loads successfully.
- Tested login using the seeded `dami` and `alice` accounts in separate browser sessions.
- Created and edited documents.
- Tested rich-text formatting, including bold, italic, headings and lists.
- Verified document persistence after refreshing the browser.
- Tested document sharing between different users.
- Confirmed that shared documents are accessible to the intended user.
- Tested TXT file upload and editing.

### Final Status

- Core document creation and editing: working.
- Document persistence: working.
- User access and sharing: tested successfully.
- File upload: tested successfully.
- Live deployment: successful.
- Automated test: previously executed successfully, with 1 test passed.

### Remaining Submission Tasks

- Finalize submission documentation.
- Package source code into a ZIP archive.
- Video not recorded in time.
- Submit the live application, repository and demonstration links.
