import json
from time import sleep

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

    def start_workflow(self, url: str, run_name: str):
        start = f"https://api.github.com/repos/{self.account}/{self.repo}/actions/workflows/githubmesh.yml/dispatches"
        s = self.session
        url_data = {"c2_url": url, "name": run_name}
        data = {"ref": "main", "inputs": url_data}
        data = json.dumps(data)
        status = s.post(start, data=data)
        if status.status_code == 204:
            pass
        else:
            print(f"Error starting workflow: {status.status_code}")
            quit()

    def check_running(self, run_name: str):
        running = f"https://api.github.com/repos/{self.account}/{self.repo}/actions/runs?status=in_progress"
        s = self.session
        found = False
        while not found:
            workflows = s.get(running)
            output = workflows.json()
            workflows = output.get("workflow_runs")
            for wf in workflows:
                if wf.get("display_title") == run_name:
                    workflow_id = wf.get("id")
                    found = True

            sleep(1)

        return workflow_id

    def cancel_workflow(self, workflow_id: str = None):
        if workflow_id:
            cancel = f"https://api.github.com/repos/{self.account}/{self.repo}/actions/runs/{workflow_id}/cancel"
            s = self.session
            s.post(cancel)
        else:
            workflow_details = self.workflow_details
            workflow_id = workflow_details.get("workflow_runs")[0].get("id")
            cancel = f"https://api.github.com/repos/{self.account}/{self.repo}/actions/runs/{workflow_id}/cancel"
            s = self.session
            s.post(cancel)
