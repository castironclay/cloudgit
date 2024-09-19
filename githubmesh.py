import json

from httpx import Client
from rich import print


class Workflow:
    def __init__(self, key, account, repo):
        self.key = key
        self.account = account
        self.repo = repo
        self.session = self.build_session(self.key)

    def build_session(self, key):
        btoken = key
        bearer = f"Bearer {btoken}"
        auth = {"Authorization": bearer}

        s = Client()
        s.headers.update({"Accept": "application/vnd.github+json"})
        s.headers.update({"X-GitHub-Api-Version": "2022-11-28"})
        s.headers.update(auth)

        return s

    def start_workflow(self, url: str):
        start = f"https://api.github.com/repos/{self.account}/{self.repo}/actions/workflows/githubmesh.yml/dispatches"
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
        running = f"https://api.github.com/repos/{self.account}/{self.repo}/actions/runs?status=in_progress"
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
        workflow_details = self.workflow_details
        workflow_id = workflow_details.get("workflow_runs")[0].get("id")
        cancel = f"https://api.github.com/repos/{self.account}/{self.repo}/actions/runs/{workflow_id}/cancel"
        s = self.session
        s.post(cancel)
