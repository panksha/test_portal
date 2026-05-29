import os
import base64
import logging
import requests
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

def report_failure_to_jira(test_name, error_message, traceback_text):
    """
    Automatically creates a high-priority bug ticket in Jira Cloud on E2E test failure.
    Reads credentials dynamically from environment variables (.env or CI/CD).
    """
    jira_base_url = os.environ.get("JIRA_BASE_URL")
    jira_user_email = os.environ.get("JIRA_USER_EMAIL")
    jira_api_token = os.environ.get("JIRA_API_TOKEN")
    jira_project_key = os.environ.get("JIRA_PROJECT_KEY", "QA")

    # If any core Jira credentials are missing, skip gracefully (normal local test run)
    if not (jira_base_url and jira_user_email and jira_api_token):
        logging.info("[Jira] Skipping automated bug filing: Jira credentials not fully loaded in environment variables or .env file.")
        return None

    # Clean the URL to avoid double slashes
    base_url = jira_base_url.rstrip("/")
    api_url = f"{base_url}/rest/api/3/issue"

    logging.info(f"[Jira] Test failure detected! Connecting to Jira Cloud to raise bug for: {test_name}")

    # Base64 encode Atlassian Basic Authentication credentials
    auth_str = f"{jira_user_email}:{jira_api_token}"
    auth_bytes = auth_str.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # Jira REST API v3 Document Format for Description (Atlassian Document Format)
    description_doc = {
        "version": 1,
        "type": "doc",
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": f"An automated E2E test case failed in the regression suite.\n\n"
                                f"Test Case ID: {test_name}\n"
                                f"Error Message: {error_message}\n\n"
                                f"Execution Environment: Local Run / CI/CD Runner\n"
                                f"Detailed Stack Trace:"
                    }
                ]
            },
            {
                "type": "codeBlock",
                "attrs": {
                    "language": "python"
                },
                "content": [
                    {
                        "type": "text",
                        "text": traceback_text
                    }
                ]
            }
        ]
    }

    # REST API v3 Payload structure for creating a Bug ticket
    payload = {
        "fields": {
            "project": {
                "key": jira_project_key
            },
            "summary": f"[BUG] Automated Test Failure: {test_name}",
            "description": description_doc,
            "issuetype": {
                "name": "Bug"
            },
            "priority": {
                "name": "High"
            },
            "labels": [
                "automated-failure",
                "regression",
                "pytest-automation"
            ]
        }
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 201:
            res_data = response.json()
            issue_key = res_data.get("key")
            issue_url = f"{base_url}/browse/{issue_key}"
            logging.info(f"[Jira] [SUCCESS] Bug ticket successfully created: {issue_key} -> {issue_url}")
            return issue_key
        else:
            logging.warning(
                f"[Jira] [ERROR] Failed to create Jira ticket. Status: {response.status_code}, Response: {response.text}"
            )
    except Exception as e:
        logging.warning(f"[Jira] [ERROR] Failed to connect to Jira Cloud API: {e}")

    return None
