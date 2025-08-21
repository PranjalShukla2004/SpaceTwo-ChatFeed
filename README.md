# SpaceTwo

Monorepo for SpaceTwo:
- `backend/` — FastAPI + Pinecone + OpenAI integration
- `frontend/` — Web client (to be added)

## Backend quickstart

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # if you have this
cp .env.example .env              # put real keys locally (never commit)
uvicorn app:app --reload --port 8000

