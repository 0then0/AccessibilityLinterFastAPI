# Accessibility Linter

A FastAPI-based service that checks HTML pages (by URL or raw HTML) against WCAG accessibility rules and returns a detailed report.

## Features

- **Pydantic**: Data validation and serialization for request/response models
- **HTML Parsing**: Uses BeautifulSoup4 with lxml parser
- **WCAG Validators**: SOLID‑compliant classes for validating:

  - Alt text on `<img>` elements (`WCAG 1.1.1`)
  - Contrast ratio for inline-styled text (`WCAG 1.4.3`)
  - Semantic structure (presence of `<header>`, `<nav>`, `<main>`, `<footer>`) (`WCAG 1.3.1`)

- **Frontend**: Simple Bootstrap-based interface

## Prerequisites

- Python 3.11 or higher
- pip

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/0then0/AccessibilityLinterFastAPI
   cd AccessibilityLinterFastAPI
   ```

2. Create and activate virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\Activate.ps1 # Windows PowerShell
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Run locally

```bash
uvicorn app.main:app --reload
```

- API docs: `http://127.0.0.1:8000/docs`
- UI: `http://127.0.0.1:8000/`

### Endpoints

- `POST /api/lint-url` — JSON payload `{ "url": "https://..." }`
- `POST /api/lint-html` — JSON payload `{ "html": "<html>..." }`
