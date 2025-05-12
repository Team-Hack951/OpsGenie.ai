import os
import requests

GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
GITLAB_PROJECT_ID = os.getenv("GITLAB_PROJECT_ID")

def trigger_pipeline(branch="main"):
    url = f"https://gitlab.com/api/v4/projects/{GITLAB_PROJECT_ID}/trigger/pipeline"
    payload = {
        "token": GITLAB_TOKEN,
        "ref": branch
    }
    response = requests.post(url, data=payload)
    return response.json()
