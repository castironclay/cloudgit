from tinydb import TinyDB, Query
from pathlib import Path
from getpass import getpass
from rich_tables import account_details
import encrypt
from rich import print


def new_account(passphrase: str) -> bool:
    home = Path.home()
    file = f"{home}/.cloudgit/cg.db"
    db = TinyDB(file)

    api_key = getpass("API Key (will be encrypted in the DB): ")
    secured_key = encrypt.encrypt_string(passphrase, api_key)
    account_name = input("Account Name: ")
    repo_name = input("Repository Name: ")
    accounts_table = db.table("accounts")
    accounts_table.insert(
        {"account_name": account_name, "api_key": secured_key, "repo_name": repo_name}
    )


def view_account(account_name: str, passphrase: str, unsafe: str = False) -> None:
    home = Path.home()
    file = f"{home}/.cloudgit/cg.db"

    db = TinyDB(file)
    table = db.table("accounts")
    account = Query()
    details = table.get(account.account_name == account_name)
    if details is None:
        print('Account does not exist')
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
    obj = Path(file)
    db = None

    if not obj.exists():
        print("Must create database first")

    else:
        db = TinyDB(file)
        db.drop_table(account_name)


def list_accounts() -> None:
    home = Path.home()
    file = f"{home}/.cloudgit/cg.db"
    obj = Path(file)
    db = None

    if not obj.exists():
        print("Must create database first")

    else:
        db = TinyDB(file)
        table = db.table('accounts')
        accounts = Query()
        print(table.search())
