# Crawler Project — NewsBreak

This project contains a **Python-based backend crawler** and a **frontend UI**, organized as two separate folders:

- backend/ — The crawler logic (Python)
- frontend/ — The user interface (JavaScript/TypeScript framework)

This README explains how to install, run, and develop each part of the project.

---

## 🚀 Quick Start

### 1. Clone the Repository

    git clone https://github.com/bvorjohan/crawler-project-newsbreak.git
    cd crawler-project-newsbreak

---

## 🐍 Backend (Crawler)

All crawler code lives inside the backend directory.

> **Important:**  
> Use **Python 3.12** for this project.  
> Some dependencies (lxml, jellyfish, etc.) do *not* yet publish wheels for Python 3.13+ or 3.14.  
> Using Python 3.12 guarantees a clean, portable installation.

### 1. Move into the backend folder

    cd backend

### 2. Create a Virtual Environment (Python 3.12)

**macOS / Linux:**

    python3.12 -m venv venv
    source venv/bin/activate

**Windows (PowerShell):**

    py -3.12 -m venv venv
    .\venv\Scripts\Activate

### 3. Install Dependencies

It is recommended to avoid cached wheels to ensure correct installs:

    python -m pip install --upgrade pip
    python -m pip install --no-cache-dir -r requirements.txt

### 4. Run the Crawler

Run the module entrypoint:

    python -m crawler.main

This will generate:

- `backend/shopify_data.json`
- `backend/extremely_straightforward_deliverable.csv`

The frontend may optionally consume the JSON file.

---

## 🌐 Frontend (Optional)

### 1. Move into the frontend folder

    cd ../frontend

### 2. Install Frontend Dependencies

    npm install

### 3. Start the Development Server

    npm run dev

Open your browser at the printed URL (commonly http://localhost:3000).

---

## 📁 Project Structure

    crawler-project-newsbreak/
    ├── backend/
    │   ├── requirements.txt
    │   ├── main.py
    │   └── ...
    ├── frontend/
    │   ├── package.json
    │   └── ...
    ├── build.sh
    ├── netlify.toml
    ├── render.yaml
    └── README.md

---

## 🧰 Developer Workflow

1. Clone repo  
2. Set up backend virtual environment (Python 3.12)  
3. Install backend dependencies  
4. Run crawler  
5. Optionally run frontend  
6. Use deployment configs if needed  

---

## 🛠 Troubleshooting

- **Wrong Python version** → Ensure you're using Python 3.12 (`python --version`)
- **Missing modules** → Activate venv and reinstall requirements  
- **Binary wheels missing** → Delete `venv` and reinstall using steps above  
- **ModuleNotFoundError (Windows)** → Confirm `where python` points inside `backend/venv/`  
- **Frontend port conflicts** → Edit `package.json` or stop conflicting service  

---

## 📦 Deployment Notes

Includes:
- netlify.toml  
- render.yaml  
- build.sh  

These are not required for local development.

---

## 📄 License

Add your desired license here.
