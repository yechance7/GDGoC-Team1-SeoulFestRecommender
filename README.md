# FindFest - Your Ultimate Guide to Seoul's Festivals and Events

Welcome to **FindFest**, a smart web application designed to help you discover the best festivals and cultural events happening in Seoul. With our AI-powered chatbot, you can get personalized recommendations tailored to your interests.

## 🌟 Overview

Finding the right event in a city as vibrant as Seoul can be overwhelming. FindFest simplifies this by providing a comprehensive, up-to-date database of events, from music festivals and art exhibitions to traditional performances and local celebrations. Our intelligent chatbot assistant makes discovery fun and interactive, helping you find the perfect event based on your mood, preferences, and schedule.

## ✨ Features

- **📅 Comprehensive Event Listings:** Browse a wide variety of events sourced directly from Seoul's public data portal.
- **🤖 AI-Powered Chatbot:** Get personalized event recommendations by chatting with our intelligent assistant powered by Upstage's Solar LLM.
- **🔍 Advanced Filtering & Search:** Easily find what you're looking for with filters for event categories, dates, and locations, plus a powerful search function.
- **❤️ Liked Events:** Save your favorite events to a personal list for quick access later.
- **🔐 User Authentication:** Sign up and log in to manage your liked events and receive a more personalized experience.
- **🔄 Automatic Updates:** Our database is automatically updated every 6 hours to ensure you always have the latest event information.

## 🚀 Technology Stack

FindFest is built with a modern and robust technology stack:

- **Backend:**
  - **Framework:** FastAPI (Python)
  - **Database:** PostgreSQL
  - **ORM:** SQLAlchemy
  - **AI & Language Models:** LangChain, Upstage Solar
- **Frontend:**
  - **Framework:** Next.js (React)
  - **Language:** TypeScript
  - **Styling:** Tailwind CSS
- **Deployment & Infrastructure:**
  - **Containerization:** Docker & Docker Compose

## 🏁 Getting Started

There are two ways to get FindFest running: using Docker (recommended for a quick setup) or setting up each service manually for development.

### Method 1: Docker (Recommended)

This is the easiest way to run the entire application. You'll need Docker and Docker Compose installed.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/GDGoC-Team1/FindFest.git
    cd GDGoC-Team1-FindFest
    ```

2.  **Environment Variables:**
    The backend requires API keys and database credentials. Copy the example environment file and fill in the required values.
    ```bash
    cp .env.example .env
    ```
    You will need to edit the `.env` file with your specific credentials.

3.  **Build and run the application:**
    Use the provided `Makefile` for easy setup.
    ```bash
    # Build the Docker images for all services
    make build

    # Start the application in detached mode
    make run
    ```

4.  **Access the application:**
    - **Frontend:** Open your browser and navigate to `http://localhost:3000`
    - **Backend API Docs:** Access the interactive API documentation at `http://localhost:8000/docs`

5.  **Stopping the application:**
    ```bash
    make stop
    ```

### Method 2: Manual Local Development Setup

This method is for developers who want to work on the frontend or backend code directly.

**Prerequisites:**
- **Node.js** (v22 or later) and **pnpm**
- **Python** (v3.10 or later) and **Poetry**
- A running **PostgreSQL** database instance.

---

#### Backend (FastAPI)

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Install Dependencies:**
    If you don't have Poetry, install it first. Then, install the project dependencies.
    ```bash
    pip install poetry
    poetry install
    ```

3.  **Set Environment Variables:**
    Create a `.env` file in the `backend` directory. You can copy the main `.env.example` from the root directory as a template. At a minimum, you must provide:
    - `DATABASE_URL`: The connection string for your PostgreSQL database.
    - `JWT_SECRET_KEY`: A secret key for signing tokens (generate a random string).
    - `SEOUL_EVENT_API_KEY`: Your API key for the Seoul Open Data Plaza.
    - `SOLAR_API_KEY`: Your API key for the Solar LLM.
    - (Other variables as needed from `app/core/config.py`)

4.  **Activate Virtual Environment and Run Server:**
    ```bash
    # Activate the shell with the virtual environment
    poetry shell

    # Run the FastAPI development server
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    The backend API will be available at `http://localhost:8000`.

---

#### Frontend (Next.js)

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install Dependencies:**
    ```bash
    pnpm install
    ```

3.  **Run the Development Server:**
    ```bash
    pnpm dev
    ```
    The frontend application will be available at `http://localhost:3000`.

4.  **Connecting to the Backend:**
    The frontend is configured to proxy API requests starting with `/api` to the backend running at `http://localhost:8000`. Ensure your backend server is running before you start the frontend.


## 🎯 Project Goal

This project was developed for the **2025 Google Developer Groups on Campus (GDGoC) oTP**. Our goal was to create an innovative and practical application that leverages the power of AI to solve a real-world problem. By combining public data with advanced language models, FindFest aims to make Seoul's rich cultural landscape more accessible and enjoyable for everyone.

---

Thank you for checking out FindFest!
