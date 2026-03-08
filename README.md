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
- Full-stack on DigitalOcean Droplet (Docker + Nginx)

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

### Full-stack on DigitalOcean Droplet

This option hosts both frontend and backend on one droplet.

1. Create a Ubuntu droplet (recommended: at least 2 GB RAM).
2. SSH into the droplet and install Docker + Compose plugin:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
	"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
	$(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
	sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

3. Clone your repo and enter it:

```bash
git clone https://github.com/yashkumar93/End-to-End-Medical-Chatbot.git
cd End-to-End-Medical-Chatbot
```

4. Create runtime env file:

```bash
cp .env.example .env
nano .env
```

Required variables in `.env`:

```ini
PINECONE_API_KEY=...
GROQ_API_KEY=...
PINECONE_HOST=...
PINECONE_INDEX_NAME=medicalbot
FLASK_SECRET_KEY=...
FRONTEND_URL=http://your_droplet_ip
HF_TOKEN=...  # optional but recommended
```

5. Build and start containers:

```bash
sudo docker compose up -d --build
```

6. Verify health:

```bash
curl http://localhost/api/health
```

Service layout:
- `nginx` serves `frontend/index.html` on port 80
- `nginx` proxies `/api/get` to Flask `/get`
- Flask runs via Gunicorn in the `app` container

Optional: enable HTTPS with a domain using Certbot + Nginx once HTTP works.

## Project Structure (Deployment)

- `app.py`: Flask backend and `/get` inference endpoint
- `render.yaml`: Render service config
- `frontend/index.html`: static UI for Vercel
- `frontend/style.css`: frontend styles
- `frontend/api/get.js`: Vercel serverless proxy to Render backend
- `frontend/vercel.json`: Vercel runtime config
- `docker-compose.yml`: local/prod compose for droplet deploy
- `Dockerfile`: backend image build
- `deploy/digitalocean/nginx.conf`: reverse proxy + static frontend serving
- `.env.example`: deployment environment variable template




