import httpx
import os

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
