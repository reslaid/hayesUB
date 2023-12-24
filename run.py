import os
import socket
import asyncio
import update
from loader import (
    Module, Loader, Utils
)


class Starter:
    def __init__(self) -> None:
        self.module = Module
        self.loader = Loader
        self.utils = Utils
        self.updater: update.Updater = update.Updater()
        self.strings: dict = {
            "text": "Run as {}@{}: {}",
            "banner_text": "HayesUB 1.3"
        }
        self.me = None
        self.login = self.get_login()
        self.name = self.get_name()

        if self.utils.Config.auto_update:
            asyncio.run(
                self.updater.update_all_files()
            )

        self.clear_console()
        self.show_banner()
        asyncio.run(self.run())

    def clear_console(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        return None

    async def show_text_banner(self):
        string = self.strings.get("text", "Run as {}: {}").format(self.login, self.name, self.me.id)
        if self.utils.Config.LoaderActions:
            self.loader.moon.debug(string)
        else:
            print(string)

    def get_login(self):
        return os.environ.get("USER", "user") if os.name != 'nt' else os.getlogin()

    def get_name(self):
        return os.environ.get("NAME", "name") if os.name != 'nt' else socket.gethostname()

    def show_banner(self):
        self.utils.Banner.show(
            text=self.strings.get("banner_text", "Hayes"),
            font='slant'
        )

    async def start_client(self):
        await self.module.client.start()
        self.me = await self.module.get_me()

        await self.module.inline.connect()
        await self.module.inline.sign_in(bot_token=Utils.Config.api_token)
        await self.module.inline.start()

    async def run_client(self):
        await Loader.hook_modules()

        await asyncio.gather(
            self.module.client.run_until_disconnected(),
            self.module.inline.run_until_disconnected()
        )

    async def run(self):
        await self.start_client()
        await self.show_text_banner()
        await self.run_client()


if __name__ == "__main__":
    Starter()
