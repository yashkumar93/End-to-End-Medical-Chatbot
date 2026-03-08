# End-to-End Medical Chatbot

RAG-based medical assistant using Flask, Pinecone, and Groq.

## Local Setup

1. Create and activate a virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Add a `.env` file in the project root.

```ini
PINECONE_API_KEY=your_pinecone_key
PINECONE_HOST=your_pinecone_host
PINECONE_INDEX_NAME=medicalbot
GROQ_API_KEY=your_groq_key
FLASK_SECRET_KEY=change_me
FRONTEND_URL=http://localhost:8080
```

4. (Optional) Populate Pinecone index.

```bash
python store_index.py
```

5. Run the backend app.

```bash
python app.py
```

## Deployment

This repository is prepared for:
- Backend on Render
- Frontend on Vercel

### Backend on Render

1. Create a new Render `Web Service` from this repo.
2. Use:

```bash
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app --bind 0.0.0.0:$PORT
```

3. Add environment variables in Render:

```ini
PINECONE_API_KEY=...
PINECONE_HOST=...
PINECONE_INDEX_NAME=medicalbot
GROQ_API_KEY=...
FRONTEND_URL=https://your-vercel-app.vercel.app
FLASK_SECRET_KEY=...
```

4. Deploy and verify:

```text
https://your-render-service.onrender.com/health
```

Note: `render.yaml` is included for optional Blueprint-based provisioning.

### Frontend on Vercel

1. Import this repo in Vercel.
2. Set `Root Directory` to `frontend`.
3. Add Vercel environment variable:

```ini
RENDER_BACKEND_URL=https://your-render-service.onrender.com
```

4. Deploy.

The frontend sends chat requests to `/api/get`, and `frontend/api/get.js` forwards them to Render securely.

## Project Structure (Deployment)

- `app.py`: Flask backend and `/get` inference endpoint
- `render.yaml`: Render service config
- `frontend/index.html`: static UI for Vercel
- `frontend/style.css`: frontend styles
- `frontend/api/get.js`: Vercel serverless proxy to Render backend
- `frontend/vercel.json`: Vercel runtime config




