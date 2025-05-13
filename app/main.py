#app/main.py
from fastapi import FastAPI, Request
from app.slack_handler import handle_slack_event

app = FastAPI()

@app.get("/")
def read_root():
    return {"msg": "Hello from FastAPI on Render"}

@app.post("/slack/events")
async def slack_events(request: Request):
    return await handle_slack_event(request)
