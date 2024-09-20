from getpass import getpass
from pathlib import Path

from rich import print
from tinydb import Query, TinyDB

import encrypt
from githubmesh import Workflow
from rich_tables import account_details, deployment_details


def new_account(passphrase: str) -> bool:
    home = Path.home()
    file = f"{home}/.cloudgit/cg.db"
    db = TinyDB(file)

    api_key = getpass("API Key (will be encrypted in the DB): ")
    secured_key = encrypt.encrypt_string(passphrase, api_key)
    account_name = input("Account Name: ")
    repo_name = input("Repository Name: ")
    account_details = db.table("account_details")
    account_details.insert(
        {"account_name": account_name, "api_key": secured_key, "repo_name": repo_name}
    )


def view_account(account_name: str, passphrase: str, unsafe: str = False) -> None:
    home = Path.home()
    file = f"{home}/.cloudgit/cg.db"

    db = TinyDB(file)
    table = db.table("account_details")
    account = Query()
    details = table.get(account.account_name == account_name)
    if details is None:
        print("Account does not exist")
        return

    repo_name = details.get("repo_name")
    api_key = details.get("api_key")

    if unsafe:
        api_key = encrypt.decrypt_string(passphrase, api_key)

    if not unsafe:
        api_key = "REDACTED"

    account_details(account_name, repo_name, api_key, unsafe)


def delete_account(account_name: str) -> None:
    home = Path.home()
    file = f"{home}/.cloudgit/cg.db"
    db = TinyDB(file)
    table = db.table("account_details")
    account = Query()
    table.remove(account.account_name == account_name)


def list_accounts() -> None:
    home = Path.home()
    file = f"{home}/.cloudgit/cg.db"

    db = TinyDB(file)
    table = db.table("account_details")
    for index, account in enumerate(table.all()):
        print(f'Account{index+1}: {account.get("account_name")}')


def list_deployments(account_name: str) -> None:
    home = Path.home()
    file = f"{home}/.cloudgit/cg.db"

    db = TinyDB(file)
    table = db.table("deployments")
    for index, deployment in enumerate(table.all()):
        if account_name == deployment.get("account_name"):
            print(f'{index+1}: {deployment.get("deploy_id")}')


def deployment_info(
    account_name: str, deploy_id: str, config: bool, wf: Workflow
) -> None:
    home = Path.home()
    file = f"{home}/.cloudgit/cg.db"

    db = TinyDB(file)
    table = db.table("deployments")
    deployment = Query()
    info = table.get(deployment.deploy_id == deploy_id)
    if config:
        wg_config = info.get("wg_config")
        wg_config = encrypt.decode_base64_to_string(wg_config).decode()

        print(wg_config)
        print("")
        print(info.get("wstunnel_command"))
    if not config:
        status = wf.check_status(info.get("workflow_id"))
        deployment_details(account_name, deploy_id, info.get("workflow_id"), status)
