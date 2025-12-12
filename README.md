# Document Toolkit Website

A complete, modern web application for document conversions and manipulations. Built with React (Frontend) and FastAPI (Backend).

## Features

- **Document to PDF**: Convert Word, Excel, PowerPoint, and Text files to PDF.
- **PDF Operations**: Merge, Split, Compress, and Remove Pages from PDFs.
- **Image Tools**: Convert Images to PDF, PDF to Images, and convert between Image formats (JPG <-> PNG).
- **Clean UI**: Modern, responsive interface built with Tailwind CSS.
- **Privacy Focused**: Files are processed in `/tmp` and automatically deleted after processing.

## Tech Stack

- **Frontend**: React, Tailwind CSS, Axios, React Router, Vite.
- **Backend**: FastAPI, Uvicorn, Python-docx, OpenPyXL, PyPDF2, Pillow, LibreOffice (headless).

## Prerequisites

- **Node.js** (v16+)
- **Python** (v3.9+)
- **LibreOffice**: Must be installed and accessible via command line (`libreoffice` or `soffice`).
  - *Linux*: `sudo apt install libreoffice`
  - *Windows*: Install from website, ensure directory is in System PATH.
- **Poppler**: Required for `pdf2image`.
  - *Linux*: `sudo apt install poppler-utils`
  - *Windows*: Download binary and add `bin` to PATH.

## Setup Instructions

### Backend

1. Navigate to server directory:
   ```bash
   cd server
   ```
2. Create virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the server:
   ```bash
   uvicorn main:app --reload
   ```
   Server runs at `http://localhost:8000`.

### Frontend

1. Navigate to client directory:
   ```bash
   cd client
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run development server:
   ```bash
   npm run dev
   ```
   Client runs at `http://localhost:5173`.

## Deployment

### Backend (VPS/Docker)
- Use a production server like Gunicorn with Uvicorn workers.
- Dockerize the application including LibreOffice and Poppler in the image.

### Frontend (Static)
- Build the project:
  ```bash
  npm run build
  ```
- Serve the `dist` folder using Nginx, Apache, or Vercel/Netlify.

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive Swagger UI documentation.
