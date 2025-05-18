import streamlit as st
import requests

BACKEND_URL = st.secrets["BACKEND_URL"]

st.set_page_config(page_title="OpsGenie.ai UI", layout ="centered")
st.markdown("""
<h1 style='text-align: center; color: #fc6d26;'>🤖 OpsGenie.ai</h1>
<h4 style='text-align: center; color: #431600;'>Your AI-powered DevOps Copilot for GitLab CI/CD</h4>
""", unsafe_allow_html=True)


st.sidebar.header("Quick Actions")

option = st.sidebar.selectbox(
    "Choose action",
    [
        "Trigger Pipeline",
        "Check Pipeline Status",
        "Cancel Pipeline",
        "List Merge Requests",
        "Show Help"
    ]
)
st.markdown("---")

col1, col2 = st.columns(2)
branch = col1.text_input("Branch", value="main")
env = col2.text_input("Environment (optional)")

if option == "Trigger Pipeline":
    service = st.text_input("Service/Component (optional)")
    version = st.text_input("Version/Tag (optional)")

    if st.button("🔥 Trigger Pipeline"):
        text = f"trigger pipeline on {branch}"
        if env:
            text += f" to {env}"
        if service:
            text += f" for {service}"
        if version:
            text += f" version {version}"

        payload = {
            "queryResult": {
                "queryText": text,
                "parameters": {
                    "branch": branch
                },
                "intent": {
                    "displayName": "TriggerPipelineIntent"
                }
            }
        }

        res = requests.post(f"{BACKEND_URL}/dialogflow/events", json=payload)
        st.success(res.json().get("fulfillmentText", "Triggered!"))

elif option == "Check Pipeline Status":
    if st.button("🔍 Check Status"):
        payload = {
            "queryResult": {
                "queryText": f"pipeline status on {branch}",
                "parameters": {
                    "branch": branch
                },
                "intent": {
                    "displayName": "PipelineStatusIntent"
                }
            }
        }
        res = requests.post(f"{BACKEND_URL}/dialogflow/events", json=payload)
        st.info(res.json().get("fulfillmentText", "Status unknown."))

elif option == "Cancel Pipeline":
    if st.button("🛑 Cancel Pipeline"):
        payload = {
            "queryResult": {
                "queryText": f"cancel pipeline on {branch}",
                "parameters": {
                    "branch": branch
                },
                "intent": {
                    "displayName": "CancelPipelineIntent"
                }
            }
        }
        res = requests.post(f"{BACKEND_URL}/dialogflow/events", json=payload)
        st.warning(res.json().get("fulfillmentText", "No pipeline found."))

elif option == "List Merge Requests":
    if st.button("📋 List MRs"):
        payload = {
            "queryResult": {
                "queryText": "show merge requests",
                "parameters": {},
                "intent": {
                    "displayName": "ListMRIntent"
                }
            }
        }
        res = requests.post(f"{BACKEND_URL}/dialogflow/events", json=payload)
        st.markdown(res.json().get("fulfillmentText", "No MRs found.").replace("\n", "  \n"))

elif option == "Show Help":
    if st.button("❓ Show Help Commands"):
        help_text = (
            "🤖 **OpsGenie Commands**:\n\n"
            "• `trigger pipeline on <branch>` - Deploy your branch\n"
            "• `pipeline status on <branch>` - Check latest CI status\n"
            "• `merge requests` - List open MRs\n"
            "• `cancel pipeline on <branch>` - Stop the latest pipeline\n"
        )
        st.markdown(help_text)


st.markdown("---")
st.markdown("<small style='color: gray;'>Built with ❤️ by Team Hack951 - Powered by Streamlit, GitLab & GCP</small>", unsafe_allow_html=True)
