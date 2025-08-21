# SpaceTwo

Monorepo for SpaceTwo:
- `backend/` — FastAPI + Pinecone + OpenAI integration
- `frontend/` — ReactJS + TailWind CSS

## Backend quickstart

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # if you have this
cp .env.example .env              # put real keys locally (never commit)
uvicorn app:app --reload --port 8000

## FrontEnd Start
cd frontend
npm run dev
