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

def trigger_pipeline(ref:str="main", variables: dict=None):
    url = f"https://gitlab.com/api/v4/projects/{GITLAB_PROJECT_ID}/trigger/pipeline"
    trigger_token = GITLAB_TRIGGER_TOKEN

    if not trigger_token:
        logger.error("Mising GitLab Trigger Token")
        return None
    
    payload = {
        "token": trigger_token,
        "ref": ref
    }

    if variables and len(variables)>0:
        for key, value in variables.items():
            payload[f"variables[{key}]"] = value

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error triggering pipeline: {e}")
        if e.response is not None:
            logger.error(f"GitLab response: {e.response.text}")
        return None


def get_pipeline_status(branch_name):

    url = f"https://gitlab.com/api/v4/projects/{GITLAB_PROJECT_ID}/pipelines"
    params = {"ref": branch_name, "per_page": 1}

    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        pipelines = response.json()
        if not pipelines:
            return None
        
        latest_pipeline = pipelines[0]
        pipeline_id = latest_pipeline["id"]

        pipeline_url = f"https://gitlab.com/api/v4/projects/{GITLAB_PROJECT_ID}/pipelines/{pipeline_id}"
        details_response = requests.get(pipeline_url, headers=HEADERS)
        details_response.raise_for_status()

        return details_response.json()

        # if pipelines:
        #     return pipelines[0]["status"]
        # else:
        #     return "No pipelines found for this branch."
    except requests.RequestException as e:
        logger.error(f"Error getting pipeline status: {e}")
        return None

# def get_pipeline_status(branch: str="main"):
#     url = f"https://gitlab.com/api/v4/projects/{GITLAB_PROJECT_ID}/pipelines?ref={branch}"

#     try:
#         response = requests.get(url,headers=HEADERS)
#         response.raise_for_status()
#         pipelines = response.json()
#         if not pipelines:
#             return None
        
#         latest_pipeline = pipelines[0]
#         pipeline_id = latest_pipeline["id"]

#         pipeline_url = f"https://gitlab.com/api/v4/projects/{GITLAB_PROJECT_ID}/pipelines/{pipeline_id}"
#         details_response = requests.get(pipeline_url, headers=HEADERS)
#         details_response.raise_for_status()

#         return details_response.json()
#     except requests.RequestException as e:
#         logger.error(f"Error getting pipeline status: {e}")
#         return None

