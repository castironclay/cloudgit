import cmd2
from cmd2 import Cmd2ArgumentParser, with_argparser
from pyfiglet import Figlet
import account
from getpass import getpass


class BasicApp(cmd2.Cmd):
    CUSTOM_CATEGORY = "CloudGit Commands"

    def __init__(self):
        super().__init__()
        # Prints an intro banner once upon application startup
        f = Figlet()
        self.intro = f.renderText("CloudGit")

        # Show this as the prompt when asking for input
        self.prompt = "cloudgit> "

        # Set the default category name
        self.default_category = "Built-in Commands"

        self.passphrase = getpass(
            "\nPlease enter a passphrase for encryption. Make sure it is something secure and memorable, as you will need it to access your data.\n**Do not lose this passphrase** — if you forget it, you will not be able to recover your encrypted information.\nInput here: "
        )

    argparser = Cmd2ArgumentParser(description="add account details")

    @with_argparser(argparser)
    @cmd2.with_category(CUSTOM_CATEGORY)
    def do_new_account(self, _):
        account.new_account(self.passphrase)

    argparser = Cmd2ArgumentParser(description="view account details")
    argparser.add_argument("account_name", help="name of account")

    @with_argparser(argparser)
    @cmd2.with_category(CUSTOM_CATEGORY)
    def do_view_account(self, arg):
        account_name = arg.account_name
        account.view_account(account_name)

    argparser = Cmd2ArgumentParser(description="update account details")
    argparser.add_argument("account_name", help="name of account")

    @with_argparser(argparser)
    @cmd2.with_category(CUSTOM_CATEGORY)
    def do_update_account(self, arg):
        account_name = arg.account_name
        account.update_account(self.passphrase, account_name)

    argparser = Cmd2ArgumentParser(description="delete account")
    argparser.add_argument("account_name", help="name of account")

    @with_argparser(argparser)
    @cmd2.with_category(CUSTOM_CATEGORY)
    def do_delete_account(self, arg):
        account_name = arg.account_name
        account.delete_account(account_name)


if __name__ == "__main__":
    app = BasicApp()
    app.cmdloop()
