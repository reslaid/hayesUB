from logger import Moon, LogLevel
from utils import Utils

import os
import asyncio
import argparse


class ConfigManager:
    def __init__(self):
        self.logger = Moon(
            self.__class__.__name__,
            Utils.Files.log_path('hayes.log'),
            stream_handler=True,
            stream_level=LogLevel.INFO,
            file_handler=True,
            file_level=LogLevel.DEBUG
        )
        self.config = Utils.Config
        self.config_path = Utils.Config.get_config_path()
        self.config_parse = Utils.Config.get_config()

        self.api_id = None
        self.api_hash = None
        self.api_token = None
        self.admin_id = None

    async def read_config(self):
        self.api_id = input("[https://my.telegram.org/] Enter API ID: ")
        self.api_hash = input("[https://my.telegram.org/] Enter API HASH: ")
        self.api_token = input("[https://t.me/botfather] Enter BOT TOKEN: ")
        self.admin_id = input("[https://t.me/getmyid_bot] Enter your ID: ")
        self.logger.debug('Data received')

    def remove_session(self):
        try:
            os.remove(f"{self.config.session_name}.session")
            os.remove(f"{self.config.inline_session_name}.session")

        except FileNotFoundError:
            self.logger.warning(
                message="Session was not found"
            )

    async def write_config(self):
        self.config_parse.set('client', 'api_id', self.api_id)
        self.config_parse.set('client', 'api_hash', self.api_hash)
        self.config_parse.set('client', 'api_token', self.api_token)
        self.config_parse.set('client', 'admin_id', self.admin_id)
        self.logger.debug('Data written to file')

    async def save_config(self):
        with open(self.config_path, 'w') as config_file:
            self.config_parse.write(config_file)

        self.logger.debug(f"File '{self.config_path}' overwritten")

    async def configure(self, remove_session=False):
        self.logger.debug(f"Authorization form called ({remove_session=})")

        if remove_session:
            self.remove_session()

        else:
            await self.read_config()
            await self.write_config()
            await self.save_config()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Configure the application.")
    parser.add_argument("--remove-session", action="store_true", help="Remove session files")
    args = parser.parse_args()

    auth = ConfigManager()
    asyncio.run(auth.configure(remove_session=args.remove_session))
