import asyncio
import aiohttp
import aiofiles
import hashlib
import os


class Updater:
    def __init__(self):
        self.base_url: str = "https://raw.githubusercontent.com/reslaid/hayesUB/main/"
        self.session: aiohttp.ClientSession = None
        self.files_to_update: list = []

    async def initialize_session(self):
        self.session = aiohttp.ClientSession()

    def update_files_list(self):
        python_files: list = [file for file in os.listdir(os.getcwd()) if file.endswith(".py")]
        self.files_to_update = python_files

    async def close_session(self):
        await self.session.close()

    async def download_file(self, url: str, local_path: str):
        async with self.session.get(url) as response:
            if response.status == 200:
                async with aiofiles.open(local_path, 'wb') as local_file:
                    await local_file.write(await response.read())

    async def calculate_file_hash(self, file_path: str):
        hasher: hashlib._Hash = hashlib.sha256()
        async with aiofiles.open(file_path, 'rb') as file:
            while chunk := await file.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    async def update_file_if_needed(self, remote_url: str, local_path: str):
        try:
            remote_hash: str = await self.calculate_remote_file_hash(remote_url)
            local_hash: str = await self.calculate_file_hash(local_path)

            if remote_hash != local_hash:
                print(f"Updating file: {local_path}")
                await self.download_file(remote_url, local_path)
            else:
                print(f"File is up to date: {local_path}")
        except Exception as e:
            print(f"Error updating file: {local_path}, {e}")

    async def calculate_remote_file_hash(self, url: str):
        async with self.session.get(url) as response:
            if response.status == 200:
                hasher = hashlib.sha256()
                hasher.update(await response.read())
                return hasher.hexdigest()

    async def update_all_files(self):
        await self.initialize_session()
        self.update_files_list()

        for file_path in self.files_to_update:
            remote_url = self.base_url + file_path
            local_path = os.path.join(os.getcwd(), file_path)

            await self.update_file_if_needed(remote_url, local_path)

        await self.close_session()


if __name__ == "__main__":
    updater = Updater()
    asyncio.run(updater.update_all_files())
