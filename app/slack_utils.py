import httpx
import os
import re

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

async def send_slack_message(channel: str, text: str):
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "channel": channel,
        "text": text
    }

    async with httpx.AsyncClient() as client:
        response = await client.post("https://slack.com/api/chat.postMessage", json=payload, headers=headers)
        if not response.json().get("ok"):
            print("Slack API error:", response.json())


def extract_branch(text: str):
    match = re.search(r"(?:branch|on)\s+([\w\-_/]+)", text)
    return match.group(1) if match else None

def extract_variables(text:str):
    variables = {}
    # Extract environment
    env_match = re.search(r"(?:to|environment)\s+(staging|production|dev|test)", text)
    if env_match:
        variables["DEPLOY_ENV"] = env_match.group(1)

    # Extract service/component
    comp_match = re.search(r"(?:for|deploy|update|restart)\s+([\w\-]+)", text)
    if comp_match:
        variables["SERVICE"] = comp_match.group(1)

    # Extract version
    ver_match = re.search(r"(?:version|tag)\s+([\w\.\-]+)", text)
    if ver_match:
        variables["VERSION"] = ver_match.group(1)

    return variables

def detect_intent_from_text(text: str) -> str:
    text = text.lower()
    if "trigger" in text or "deploy" in text:
        return "TriggerPipelineIntent"
    elif "cancel" in text:
        return "CancelPipelineIntent"
    elif "status" in text:
        return "PipelineStatusIntent"
    elif "merge request" in text or "pull request" in text or "mr" in text:
        return "ListMRIntent"
    else:
        return "FallbackIntent"