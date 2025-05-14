import os
import requests
import logging

GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
GITLAB_PROJECT_ID = os.getenv("GITLAB_PROJECT_ID")
GITLAB_TRIGGER_TOKEN = os.getenv("GITLAB_TRIGGER_TOKEN")

logger = logging.getLogger(__name__)

HEADERS = {
    "PRIVATE-TOKEN": GITLAB_TOKEN
}

def trigger_pipeline(branch:str="main", variables: dict=None):
    url = f"https://gitlab.com/api/v4/projects/{GITLAB_PROJECT_ID}/trigger/pipeline"
    trigger_token = GITLAB_TRIGGER_TOKEN

    if not trigger_token:
        logger.error("Mising GitLab Trigger Token")
        return None
    
    payload = {
        "token": trigger_token,
        "ref": branch
    }

    if variables:
        for key, value in variables.items():
            payload[f"variables[{key}]"] = value

    try:
        response = requests.post(url, data=payload, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error triggering pipeline: {e}")
        return None
    

