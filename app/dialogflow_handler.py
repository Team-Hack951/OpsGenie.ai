from fastapi import Request
from fastapi.responses import JSONResponse
from app.gitlab import (
trigger_pipeline,
cancel_running_pipeline,
get_pipeline_status,
get_open_merge_requests
)

async def handle_dialogflow_webhook(request: Request):
    payload= await request.json()
    intent = payload["queryResult"]["intent"]["displayName"]
    parameters = payload["queryResult"]["parameters"]
    user = payload.get("originalDetectIntentRequest" ,{}).get("payload",{}).get("data",{}).get("user",{})

    if intent == "TriggerPipelineIntent":
        branch = parameters.get("branch", "main")
        trigger_pipeline(branch)
        return JSONResponse(content={"fulfillmentText": f"✅ Triggered pipeline for '{branch}'."})

    elif intent == "CancelPipelineIntent":
        branch = parameters.get("branch", "main")
        success = cancel_running_pipeline(branch)
        msg = f"🛑 Cancelled pipeline on {branch}." if success else f"No running pipeline found on {branch}."
        return JSONResponse(content={"fulfillmentText": msg})

    elif intent == "PipelineStatusIntent":
        branch = parameters.get("branch", "main")
        status = get_pipeline_status(branch)
        if status:
            state = status.get("status", "unknown")
            url = status.get("web_url", "")
            msg = f"Pipeline on '{branch}': {state}\n{url}"
        else:
            msg = f"Could not fetch pipeline status for {branch}."
        return JSONResponse(content={"fulfillmentText": msg})
        #return JSONResponse(content={"fulfillmentText": f"Pipeline status for '{branch}': {status}"})

    elif intent == "ListMRIntent":
        mrs = get_open_merge_requests()
        if not mrs:
            msg = "No open merge requests."
        else:
            msg = "📋 Open MRs:\n" + "\n".join([f"- {mr['title']} ({mr['web_url']})" for mr in mrs])
        return JSONResponse(content={"fulfillmentText": msg})

    return JSONResponse(content={"fulfillmentText": "🤖 Sorry, I didn’t understand that."})