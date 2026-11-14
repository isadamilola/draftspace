# Development Log

## Project: DraftSpace – Collaborative Document Editor

### 1. Project Overview

Building a lightweight collaborative document editor inspired by Google Docs as part of the Ajaia LLC AI-Native Full Stack Developer assessment.

The application allows users to create, manage, edit, upload, and share documents.

### 2. Technology Stack

- Backend: Python with Flask
- Database: SQLite
- Frontend: HTML, CSS, JavaScript
- Rich-text editor: Quill.js (CDN)
- Authentication: Mocked login using Flask sessions
- Testing: pytest
- Deployment target: PythonAnywhere

### 3. Authentication Decision

Implemented mocked authentication using three seeded users:

- dami
- alice
- bob

Users select a demo account from a login dropdown. Flask sessions maintain the selected user's identity.

No passwords or production authentication system are implemented. This is a deliberate scope decision permitted by the assessment.

### 4. Database Design

Created three database tables:

**users**

- Stores available demo users.
- Each user has a unique username.

**documents**

- Stores document titles and HTML content.
- Records document ownership.
- Tracks creation and last-update timestamps.

**shares**

- Records which users have access to shared documents.
- Uses foreign keys to maintain relationships.
- Prevents duplicate sharing records for the same document and user.

SQLite foreign-key enforcement is enabled on database connections.

### 5. Implemented Features

**Login and sessions**

- Login page with a demo-user dropdown.
- Session-based user identification.
- Logout functionality.

**Dashboard**

- Displays documents owned by the logged-in user.
- Displays documents shared with the logged-in user.
- Shows document titles and update timestamps.
- Provides a new-document action.

**Document creation**

- Creates a new document with the default title "Untitled document".
- Automatically assigns ownership to the logged-in user.
- Redirects to the newly created document.

**Document access control**

- Implemented `get_doc_for_user(doc_id, user_id)`.
- Checks document ownership and sharing permissions.
- Returns the document and its role (`owner` or `shared`).
- Returns no document when access is not permitted.
- Unauthorized document requests return HTTP 404 to avoid revealing document existence.

### 6. Automated Testing

Created a pytest test for document access control.

The test verifies:

- A document owner can access their document.
- An unrelated user cannot access it.
- A user granted access through the shares table can access it.
- A third user without permission remains blocked.

**Latest test result:**

- 1 test passed.
- 1 warning reported.
- Execution time: 1.09 seconds.

### 7. AI-Assisted Development Workflow

AI assistants were used to:

- Help design the database schema.
- Generate and review Flask application code.
- Implement session-based mocked authentication.
- Build document ownership and sharing access checks.
- Review SQL queries and improve database access logic.
- Develop the automated access-control test.
- Explain implementation decisions and identify potential security issues.

The generated code was reviewed, integrated, executed, and tested during development.

### 8. Current Project Status

Implemented:

- Database schema and initialization.
- Seeded demo users.
- Mocked login and logout.
- Flask session management.
- Login protection.
- Document dashboard.
- Document creation.
- Document ownership and sharing access checks.
- Automated access-control test.

Not yet implemented:

- Rich-text document editor.
- Saving and reopening edited content.
- Document renaming.
- Sharing interface.
- File uploads.
- Deployment.
- Final documentation and walkthrough video.

### 9. Next Development Step

Build the document editor using Quill.js, including:

- Rich-text formatting.
- Loading existing document content.
- Saving edited content to SQLite.
- Reopening saved documents.
- Access-controlled editing routes.
