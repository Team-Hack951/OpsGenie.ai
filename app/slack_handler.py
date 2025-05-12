import hmac
import hashlib
import time
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from app.config import SLACK_SIGNING_SECRET

async def handle_slack_event(request: Request):
    body = await request.body()
    headers = request.headers

    # slack verification
    if not verify_slack_request(headers, body):
        return Response(content="Invalid request signature", status_code=403)
    
    payload = await request.json()
    if "challenge" in payload:
        return JSONResponse(content={"challenge": payload["challenge"]})

    # Respond to slacks url verification challenge
    event = payload.get("event", {})
    if event.get("type") == "app_mention":
        # respond or trigger pipeline here later
        print(f"Received message: {event.get('text')}")
    
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