import hmac
import hashlib
import time
import logging
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from app.config import SLACK_SIGNING_SECRET
from app.slack_utils import send_slack_message, extract_branch, extract_variables
from app.gitlab import trigger_pipeline, get_pipeline_status, get_open_merge_requests, cancel_running_pipeline

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

        await route_command(text,channel,user)
    
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


async def route_command(text:str, channel:str, user:str):
    text = text.lower()
    logger.info(f"Routing command: {text}")

    if "trigger pipeline" in text:
        branch = extract_branch(text) or "main"
        variables = extract_variables(text)
        result = trigger_pipeline(ref=branch, variables=variables)

        if result:
            message  = f"Pipeline triggered on branch '{branch}'.\n {result.get('web_url')}"
        else:
            message = f"Failed to trigger the pipeline."

        await send_slack_message(channel, f"<@{user}> {message}")

    elif "pipeline status" in text:
        branch = extract_branch(text) or "main"
        status = get_pipeline_status(branch)

        if status:
            state = status.get("status", "unknown")
            url = status.get("web_url", "")
            message = f"Latest pipeline on `{branch}`: `{state}`\n {url}"
        else:
            message = "Could not fetch pipeline status."

        await send_slack_message(channel, f"<@{user}> {message}")

    elif "merge requests" in text:
        mrs = get_open_merge_requests()
        if not mrs:
            message = f"There are no open merge requests."
        else:
            message = f"*Open MRs:*\n" + "\n".join([f"- <{mr['web_url']}|{mr['title']}>" for mr in mrs])

        await send_slack_message(channel, f"<@{user}> {message}")

    elif "cancel pipeline" in text:
        branch = extract_branch(text) or "main"
        result = cancel_running_pipeline(branch_name=branch)
        message = f"Pipeline on `{branch}` cancelled." if result else " No running pipeline to cancel."

        await send_slack_message(channel, f"<@{user}> {message}")
        
    elif "hello" in text:
        await send_slack_message(channel, f"Hello <@{user}>!")

    elif "help" in text:
        msg = (
        "🤖 *PromptOps Commands*:\n"
        "• `trigger pipeline on <branch>` - deploy your branch\n"
        "• `pipeline status on <branch>` - check latest CI status\n"
        "• `merge requests` - list open MRs\n"
        "• `cancel pipeline on <branch>` - stop the latest pipeline\n"
        "• `hello` - say hi\n"
    )
        await send_slack_message(channel, f"<@{user}> {msg}")
