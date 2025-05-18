#app/main.py
import logging
from fastapi import FastAPI, Request
from app.slack_handler import handle_slack_event
from app.dialogflow_handler import handle_dialogflow_webhook

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

app = FastAPI()

@app.get("/")
def read_root():
    return {"msg": "Hello from FastAPI on Render"}

@app.post("/slack/events")
async def slack_events(request: Request):
    return await handle_slack_event(request)

@app.post("/dialogflow/events")
async def dialogflow_events(request: Request):
    return await handle_dialogflow_webhook(request)