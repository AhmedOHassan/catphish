# Catphish: Multi-Layer Voice Verification & Anti-Deepfake System

Catphish is a proof-of-concept platform for **voice-based user authentication and anti-deepfake detection**, including demo web apps, API backend, and a 4-layer verification system to prevent AI-generated audio attacks.

![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react&logoColor=fff)

---

## Project Trailer

[Click here to watch the trailer](product-trailer/Catphish_Trailer.mp4)

---

## Project Link
https://catphish.vercel.app/

---

## 🏗 Project Structure

```
/
├── api/                          # API server code (Python FastAPI)
├── catphish-api/                 # React client for voice verification
├── voice-detection-demo/         # 4-layer Python verification demo
│   └── test_audio/               # Audio sample instructions
├── demo-website/                 # Demo banking webapp (React)
├── db/                           # Database resources (Valkey/Redis)
├── docker-compose.yml            # Multi-service orchestration
├── scripts/                      # Utility scripts
├── docs/                         # Internal documentation
├── product-site/                 # Marketing site
├── product-trailer/              # Testing Verification
```

---

## 🎯 What is Catphish?

Catphish demonstrates secure user authentication with _voice biometrics_, focusing on identifying and thwarting AI-generated (deepfake) audio attacks. The system includes:
- **Voice enrollment and verification (real and simulated)**
- **API backend with Python and FastAPI**
- **2-layer defense:**
  - Speaker verification
  - Comprehension: Google Gemini AI for phrase analysis
- **Demo web apps and banking site for real-world workflows**

---

## 🚀 Quick Start

### 1. Catphish API Backend (Python)

```bash
docker compose up # Start Valkey
./scripts/seed-valkey.sh # Seed data
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 # Start API
```

### 2. Catphish API Frontend (React)

```bash
cd catphish-api
npm install
npm run dev
```
Opens on http://localhost:3001

### 3. SecureBank Demo Site

```bash
cd demo-website
npm install
npm run dev
```
Opens on http://localhost:3000

This site demonstrates integration with Catphish for secure flow (sign up, login, bank dashboard, voice verification prompt).

---

## 🛡 Features

- **Layered voice authentication:** Combines multiple voice/ML checks for robust security.
- **Deepfake detection:** Blocks many common attacks by distinguishing synthetic from real speech.
- **Web-based demo:** See verification flows and banking integration in the browser (React).
- **API-centric design:** Modular backend for future real deployments.
- **Dockerized:** Orchestrate backend/frontend/Redis (Valkey) with one command.

---

## 🧪 Example User Flows

### Voice Verification Web UI

- **New user:** Prompted to enroll voice sample.
- **Returning user:** Prompts for verification phrase, simulates attack/failure scenarios.
- **Demo site:** Bank website UI triggers verification via REST API and redirects to Catphish for secure voice check.

---

## 👨‍💻 Authors & Credits

Catphish is maintained by AhmedOHassan, Tristan Curtis, Rameez Malik, Nolan Witt
