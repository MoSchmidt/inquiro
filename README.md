<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="frontend/src/assets/images/inquiro_logo_dark_mode.svg">
    <source media="(prefers-color-scheme: light)" srcset="frontend/src/assets/images/inquiro_logo.svg">
    <img alt="Inquiro" src="frontend/src/assets/images/inquiro_logo.svg" width="350">
  </picture>
</p>

<p align="center">
  <em>AI-powered research discovery platform that matches your research interests with relevant scientific papers using intelligent semantic ranking.</em>
</p>

---

## 📋 Prerequisites

| Tool | Required For | Installation |
| --- | --- | --- |
| **Docker** | All setups | [docker.com](https://www.docker.com/products/docker-desktop/) |
| **Python** | 3.11.14 — Development setup only | [python.org](https://www.python.org/downloads/release/python-31114/) |
| **Node.js** | 22.12.0+ — Development setup only | [nodejs.org](https://nodejs.org/) |

You also need an **OpenAI API key** for semantic ranking and paper analysis features.
Get one at [platform.openai.com](https://platform.openai.com/).

---

## 🚀 Quick Start (Docker)

Run the entire stack — database, backend, frontend, and test data seeding — in Docker with a few commands.

1. **Create your environment file:**

   ```bash
   cp .env.example .env
   ```

2. **Add your OpenAI API key** by editing the `.env` file:

   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

3. **Start all services:**

   ```bash
   docker compose --profile full up -d
   ```

   This will automatically:
   - Start the PostgreSQL database (with pgvector)
   - Launch the backend, which creates the database schema on startup
   - Seed the database with test papers and a test user (`test` / `My Test Project`)
   - Serve the frontend via nginx

Once running, open [http://localhost](http://localhost) in your browser.

| Service | URL |
| --- | --- |
| Frontend | [http://localhost](http://localhost) |
| Backend API | [http://localhost:8000](http://localhost:8000) |
| API Docs | [http://localhost:8000/docs](http://localhost:8000/docs) |

> To stop all services: `docker compose --profile full down`

---

## 🛠️ Development Setup

For active development, run only the database in Docker and start the frontend and backend manually. This gives you hot-reload and direct access to the code.

### 🖥️ Frontend

1. **Navigate to the frontend directory:**

   ```bash
   cd frontend
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Start the development server:**

   ```bash
   npm run dev
   ```

   The frontend will be available at [http://localhost:5173](http://localhost:5173) (or the port shown in the console).

### ⚙️ Backend

1. **From the project root, start the database:**

   ```bash
   docker compose up -d
   ```

2. **Navigate to the backend directory:**

   ```bash
   cd backend
   ```

3. **Set up a Python environment** *(optional but recommended)*

   Choose **either** a standard `venv` **or** an Anaconda environment.

   <details>
   <summary><strong>Option A — venv (Python 3.11.14)</strong></summary>

   Ensure Python **3.11.14** is available on your system (`python --version` or `python3 --version`).

   **Linux / macOS:**

   ```bash
   python3.11 -m venv inquiro-env
   source inquiro-env/bin/activate
   ```

   **Windows (PowerShell):**

   ```bash
   py -3.11 -m venv inquiro-env
   inquiro-env\Scripts\activate
   ```

   </details>

   <details>
   <summary><strong>Option B — Anaconda</strong></summary>

   ```bash
   conda create -n inquiro-env python=3.11.14
   conda activate inquiro-env
   ```

   This ensures all dependencies install cleanly — especially libraries like `torch`, `transformers`, and scientific packages.

   </details>

4. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

5. **Create a local environment file:**

   Copy the example file and rename it to `dev.env`:

   **Linux / macOS:**

   ```bash
   cp .env.example dev.env
   ```

   **Windows (PowerShell):**

   ```bash
   copy .env.example dev.env
   ```

   Then open `dev.env` and add your **OpenAI API key**. Adjust other values if needed (e.g., database port, credentials).

6. **Install Git hooks:**

   ```bash
   pre-commit install
   ```

   After this, formatters and linters will run automatically on every commit.

7. **Start the FastAPI server:**

   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at [http://localhost:8000](http://localhost:8000)
   API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 API Testing with Bruno

The project includes a [**Bruno**](https://www.usebruno.com) collection under `/bruno` for testing and exploring the backend API. Bruno is a lightweight, file-based API client that stores requests in plain text, making it well-suited for collaborative development and version control.

1. **Install Bruno** — Download from [usebruno.com/downloads](https://www.usebruno.com/downloads).

2. **Open the collection** — Launch Bruno, click **"Open Collection"**, and select the `/bruno/Inquiro Bruno` folder from the project root.

3. **Select an environment** — The `/bruno/Inquiro Bruno/environments` directory contains predefined environment files. For local development, select the **_Development_** environment.

---

## 🤖 AI Acknowledgement

AI-assisted tools, including ChatGPT, Claude (Code), and Cursor, were used during the development of this project for architectural planning, code generation, and debugging support. All AI-generated output was reviewed and adapted by the development team.