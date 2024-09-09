import yaml
from time import sleep
from httpx import Client
import json
from rich import print


def read_creds_file():
    with open("keys.yaml", "r") as creds_file:
        all_creds = yaml.safe_load(creds_file)

    return all_creds


class Workflow:
    def __init__(self, account_details):
        self.details = account_details
        self.session = self.build_session(self.details)

    def build_session(self, creds):
        btoken = creds.get("key")
        bearer = f"Bearer {btoken}"
        auth = {"Authorization": bearer}

        s = Client()
        s.headers.update({"Accept": "application/vnd.github+json"})
        s.headers.update({"X-GitHub-Api-Version": "2022-11-28"})
        s.headers.update(auth)

        return s

    def start_workflow(self, url: str):
        details = self.details
        start = f'https://api.github.com/repos/{details.get("account")}/{details.get("repo")}/actions/workflows/{details.get("file")}/dispatches'
        s = self.session
        url_data = {"c2_url": url}
        data = {"ref": "main", "inputs": url_data}
        data = json.dumps(data)
        status = s.post(start, data=data)
        if status.status_code == 204:
            pass
        else:
            print(f"Error starting workflow: {status.status_code}")
            quit()

    def check_running(self):
        details = self.details
        running = f'https://api.github.com/repos/{details.get("account")}/{details.get("repo")}/actions/runs?status=in_progress'
        s = self.session
        total_count = 0

        # Check until we see a workflow in progress
        while total_count == 0:
            active_workflow = s.get(running)
            output = active_workflow.json()
            total_count = output.get("total_count")

        active_workflow = s.get(running)
        self.workflow_details = active_workflow.json()

    def cancel_workflow(self):
        details = self.details
        workflow_details = self.workflow_details
        workflow_id = workflow_details.get("workflow_runs")[0].get("id")
        cancel = f"https://api.github.com/repos/{details.get("account")}/{details.get("repo")}/actions/runs/{workflow_id}/cancel"
        s = self.session
        s.post(cancel)


if __name__ == "__main__":
    # For testing only to ensure workflows are starting.
    # Throwaway C2 URL used
    # Will auto-cancel the workflow
    creds = read_creds_file()
    for account in creds.keys():
        print("Starting workflow")
        details = creds.get(account)
        work = Workflow(details)
        work.start_workflow("https://www.google.com")
        work.check_running()
        print("workflow started")
        sleep(10)
        print("workflow cancelled")
        work.cancel_workflow()
