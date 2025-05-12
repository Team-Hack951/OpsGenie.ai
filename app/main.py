from fastapi import FastAPI, Request
from app.slack_handler import handle_slack_event

app = FastAPI()

@app.post("/slack/events")
async def slack_events(request: Request):
    return await handle_slack_event(request)