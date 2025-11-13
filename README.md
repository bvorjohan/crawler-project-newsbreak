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

### 1. Move into the backend folder

    cd backend

### 2. Create a Virtual Environment

**macOS / Linux:**

    python3 -m venv venv
    source venv/bin/activate

**Windows (PowerShell):**

    python -m venv venv
    .\venv\Scripts\Activate

### 3. Install Dependencies

    pip install -r requirements.txt

### 4. Run the Crawler

Depending on your entry point, run:

    python main.py

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
2. Set up backend virtual environment
3. Install backend dependencies
4. Run crawler
5. Optionally run frontend
6. Use deployment configs if needed

---

## 🛠 Troubleshooting

- Missing modules: activate environment and reinstall requirements.
- ModuleNotFoundError: ensure you're in backend.
- Frontend port conflicts: edit package.json or stop conflicting service.
- Missing config: provide config.example.env.

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
