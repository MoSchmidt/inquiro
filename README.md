# Inquiro

*Inquiro* is an AI-powered research discovery platform designed to match user research interests with relevant scientific papers using intelligent semantic ranking.

---

## ⚙️ Development Setup

### 🧩 Prerequisites

Make sure the following tools are installed on your system:

| Tool                    | Recommended Version | Installation Link                                                                                   |
| ----------------------- |---------------------|-----------------------------------------------------------------------------------------------------|
| **Docker**              | Latest              | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)               |
| **Python**              | 3.11.14             | [python.org/downloads/release/python-31114](https://www.python.org/downloads/release/python-31114/) |
| **Node.js**             | TBD                 | [nodejs.org](https://nodejs.org/)                                                                   |

💡 **Note:** Docker is only required to run the PostgreSQL database locally.
The backend and frontend are started manually.

---

## 🖥️ Frontend Setup

1. **Navigate to the frontend directory**:

   ```bash
   cd frontend
   ```
2. **Install dependencies**:

   ```bash
   npm install
   ```
3. **Start the development server**:

   ```bash
   npm run dev
   ```

   The frontend will be available at [http://localhost:5173](http://localhost:5173) (or the port shown in the console).

---

## ⚙️ Backend Setup

1. **From the project root, start the database**:

   ```bash
   docker compose up -d
   ```
2. **Navigate to the backend directory**:

   ```bash
   cd backend
   ```

Here is a clean, professional, and minimal update for that section — giving users **two clear options**:
(1) standard `venv` with the correct Python version, or
(2) Anaconda environment with the correct version.

You can paste this directly into your README.

---

## (Optional but recommended) Create and activate a Python environment

You can choose **either** a standard `venv` (recommended if you already installed Python 3.11.14 manually) **or** an Anaconda environment.

### ✅ Option A — Create a virtual environment using `venv` (Python 3.11.14)

Ensure Python **3.11.14** is available on your system (check with `python --version` or `python3 --version`).

🧠 **Linux / macOS**

```bash
# Create a virtual environment using the correct Python version
python3.11 -m venv inquiro-env

# Activate it
source inquiro-env/bin/activate
```

🪟 **Windows (PowerShell)**

```bash
# Create a virtual environment
py -3.11 -m venv inquiro-env

# Activate it
inquiro-env\Scripts\activate
```

---

### ✅ Option B — Create an environment using Anaconda (Python 3.11.14)

If you're using Conda, you can create a dedicated environment:

```bash
conda create -n inquiro-env python=3.11.14
conda activate inquiro-env
```

This ensures all dependencies install cleanly—especially libraries like `torch`, `transformers`, and scientific packages.


4. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```
   
5. **Create a local environment file**:

    Copy the example file and rename it to dev.env:

   🧠 Linux / macOS
    
    ```bash
   cp .env.example dev.env
   ```
    
   🪟 Windows (PowerShell)

   ```bash
   copy .env.example dev.env
   ```
    
   Then adjust the values if needed (e.g., database port, credentials).

6. **Install Git hooks**:

   ```bash
   pre-commit install
   ```

   After this, the formatters and linters will run automatically every time you commit.

7. **Start the FastAPI server**:

   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at [http://localhost:8000](http://localhost:8000)
   API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 API Testing with Bruno

The *Inquiro* project includes a [**Bruno**](https://www.usebruno.com) collection under `/bruno` for testing and exploring the backend API.
Bruno is a lightweight, file-based API client that stores requests in plain text, making it well-suited for collaborative development and version control.

### ⚙️ Setup

1. **Install Bruno**

   Download and install Bruno from [usebruno.com/downloads](https://www.usebruno.com/downloads).

2. **Open the collection**

   * Launch Bruno.
   * Click **“Open Collection”** and select the `/bruno/Inquiro Bruno` folder from the project root.

3. **Select or configure an environment**

   The `/bruno/Inquiro Bruno/environments` directory contains predefined environment files. For local development select the **_Development_** environment.


### 🚀 Basic Usage

Before authenticating, a user must be created:

1. Run the **Users → Create User** request and provide only a `username` in the request body.
2. Next, use the **Authentication → Login** request with the same `username` to obtain an access and refresh token.
