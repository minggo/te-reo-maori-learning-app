# te-reo-maori-learning-app
Te Reo Māori Learning Web Application

## Local Development & Testing

### Prerequisites

- Docker & Docker Compose  
- Python 3.10+ (if you run without Docker)  
- (Optional) A running MongoDB instance if not using Docker  

---

### Option A: Docker Compose

> **Run all of the following commands from the `server/` directory.**

1. **Copy or create your `.env`** file next to `docker-compose.yml`:

   ```dotenv
   # .env
   MONGO_URI=mongodb://mongo:27017
   DB_NAME=te_reo_test_db

   # SMTP (email) settings—replace with your own SMTP server
   SMTP_HOST=smtp.your.com
   SMTP_USER=you@your.com
   SMTP_PASSWORD=secret
   SMTP_SENDER=you@your.com

2. **Start services:**

   ```bash
   # from the server/ directory
   chmod +x start_local.sh       # if not already executable
   ./start_local.sh              # this only brings up mongo
   docker-compose up --build     # then start both mongo + fastapi
   ```
   - Your FastAPI app will be available at http://localhost:8000/docs.
   - Any code changes in `server/` are reflected automatically thanks to --reload.

### Option B: Host Python & MongoDB

1. **Clone & venv:**

   ```bash
   cd te-reo-maori-learning-app/server
   python -m venv .venv
   source .venv/bin/activate        # Windows: .\.venv\Scripts\activate
   ```
2. **Install dependencies:**
   
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt -r dev-requirements.txt
   ```

3. **Start MongoDB** (if you don’t already have one):

   ```bash
   docker run -d --name maori-mongo \
   -p 27017:27017 \
   -v maori-mongo-data:/data/db \
   mongo:latest
   ```

4. **Set your environment variables** (same `.env` as above). If you’re not using Docker Compose, source it:

   ```bash
   export $(grep -v '^#' .env | xargs)
   ```

5. **Run the app:**

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Run tests:**

   ```bash
   pytest -q
   ```

### What each environment variable does

- `MONGO_URI`: connection string for MongoDB (e.g. `mongodb://mongo:27017`)
- `DB_NAME`: name of the database your tests and app will use (e.g. te_reo_test_db)
- `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_SENDER`: credentials for your SMTP server (used by auth/email features)

> **Tip**: If you don’t need email functionality in local dev or CI, you can leave the SMTP vars blank and update your Settings class to make them optional so the server still starts without errors.

That’s it—once your environment is up and variables set, you can explore your API at `/docs` and validate everything with `pytest`.






