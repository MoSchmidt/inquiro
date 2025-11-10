# Inquiro

*Inquiro* is an AI-powered research discovery platform designed to match user research interests with relevant scientific papers using intelligent semantic ranking.

---

## ⚙️ Development Setup

### 🧩 Prerequisites

Make sure the following tools are installed on your system:

| Tool                    | Recommended Version | Installation Link                                                                                 |
| ----------------------- | ------------------- | ------------------------------------------------------------------------------------------------- |
| **Docker**              | Latest              | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)             |
| **Python**              | 3.14.0              | [python.org/downloads/release/python-3140](https://www.python.org/downloads/release/python-3140/) |
| **Node.js**             | TBD                 | [nodejs.org](https://nodejs.org/)                                                                 |

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

3. **(Optional but recommended) Create and activate a virtual environment named `inquiro-env`**:

   🧠 Linux / macOS

   ```bash
   # Create a virtual environment
   python -m venv inquiro-env

   # Activate it
   source inquiro-env/bin/activate
   ```

   🪟 Windows (PowerShell)

   ```bash
   # Create a virtual environment
   python -m venv inquiro-env

   # Activate it
   inquiro-env\Scripts\activate
   ```


4. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
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
