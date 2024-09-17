from tinydb import TinyDB
from pathlib import Path
from loguru import logger
from getpass import getpass
import encrypt


def new_account(passphrase: str) -> bool:
    home = Path.home()
    file = f"{home}/.cloudgit/cg.db"
    obj = Path(file)
    db = None

    if not obj.exists():
        print("Initializing database...")
        try:
            db_dir = Path(f"{home}/.cloudgit")
            db_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger(e)

        db = TinyDB(f"{home}/.cloudgit/cg.db")

    else:
        db = TinyDB(file)

    api_key = getpass("API Key (will be encrypted in the DB): ")
    secured_key = encrypt.encrypt_string(passphrase, api_key)
    account_name = input("Account Name: ")
    repo_name = input("Repository Name: ")
    new_table = db.table(account_name)
    new_table.insert(
        {"account_name": account_name, "api_key": secured_key, "repo_name": repo_name}
    )


def view_account(account_name: str) -> None:
    home = Path.home()
    file = f"{home}/.cloudgit/cg.db"
    obj = Path(file)
    db = None

    if not obj.exists():
        print("Must create database first")

    else:
        db = TinyDB(file)

        table = db.table(account_name)
        details = table.all()

        print(details)

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

def update_account(passphrase: str, account_name: str) -> None:
    home = Path.home()
    file = f"{home}/.cloudgit/cg.db"
    obj = Path(file)
    db = None

    if not obj.exists():
        print("Must create database first")

    else:
        db = TinyDB(file)

        api_key = getpass("API Key (will be encrypted in the DB): ")
        secured_key = encrypt.encrypt_string(passphrase, api_key)
        new_account_name = input("Account Name: ")
        repo_name = input("Repository Name: ")
        db.drop_table(account_name)
        new_table = db.table(account_name)
        new_table.insert(
            {"account_name": new_account_name, "api_key": secured_key, "repo_name": repo_name}
        )
