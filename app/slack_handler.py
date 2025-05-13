import hmac
import hashlib
import time
import logging
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from app.config import SLACK_SIGNING_SECRET

logger = logging.getLogger(__name__)

async def handle_slack_event(request: Request):
    body = await request.body()
    headers = request.headers

    # Slack signature verification
    if not verify_slack_request(headers, body):
        return Response(content="Invalid request signature", status_code=403)
    
    payload = await request.json()
    logger.info(f"Slack event payload: {payload}")

    # URL verification during initial setup
    if "challenge" in payload:
        return JSONResponse(content={"challenge": payload["challenge"]})

    event = payload.get("event", {})
    event_type = event.get("type")

    if event_type in ["app_mention", "message"]:
        user = event.get("user")
        text = event.get("text")
        channel = event.get("channel")
        logger.info(f"Received {event_type} from {user} in {channel}: {text}")

        # You will add response logic or intent handling here later
    
    return {"status": "ok"}

def verify_slack_request(headers, body):
    timestamp = headers.get("x-slack-request-timestamp")
    if abs(time.time() - int(timestamp)) > 60 * 5:
        return False

    sig_basestring = f"v0:{timestamp}:{body.decode()}"
    my_signature = (
        "v0=" + hmac.new(
            SLACK_SIGNING_SECRET.encode(),
            sig_basestring.encode(),
            hashlib.sha256
        ).hexdigest()
    )

    slack_signature = headers.get("x-slack-signature")
    return hmac.compare_digest(my_signature, slack_signature)