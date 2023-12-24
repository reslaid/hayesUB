import asyncio
import aiohttp
import aiofiles
import argparse
import hashlib
import os


class Updater:
    def __init__(self):
        self.base_url: str = "https://raw.githubusercontent.com/reslaid/hayesUB/main/"
        self.repo_url: str = "https://api.github.com/repos/reslaid/hayesUB/contents/"
        self.session: aiohttp.ClientSession = None
        self.valid_extensions = [".py", ".pyc", ".sh", ".bat", ".txt"]
        self.files_to_update: list = []
        self.repository_files: list = []

    async def initialize_session(self):
        self.session = aiohttp.ClientSession()

    async def update_files_list(self):
        all_files = [f for f in os.listdir(os.getcwd()) if os.path.isfile(os.path.join(os.getcwd(), f))]
        self.files_to_update = [file for file in all_files if any(file.lower().endswith(ext) for ext in self.valid_extensions)]
        self.repository_files = await self.get_repository_files()

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

    async def get_repository_files(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.repo_url) as response:
                if response.status == 200:
                    data = await response.json()
                    files = [item["name"] for item in data if item["type"] == "file"]
                    return files
                else:
                    print(f"Failed to retrieve files. Status code: {response.status}")
                    return []

    async def check_files(self):
        await self.initialize_session()
        await self.update_files_list()

        for file_path in self.files_to_update:
            remote_url = self.base_url + file_path
            local_path = os.path.join(os.getcwd(), file_path)

            if file_path not in self.repository_files:
                print(f"File not found in the repository: {local_path}")

            elif not os.path.exists(local_path):
                print(f"Local file is missing: {local_path}")

            else:
                local_hash = await self.calculate_file_hash(local_path)
                remote_hash = await self.calculate_remote_file_hash(remote_url)

                if local_hash != remote_hash:
                    print(f'The file is out of date: {local_path}')

        await self.close_session()

    async def update_all_files(self):
        await self.initialize_session()
        await self.update_files_list()

        for file_path in self.files_to_update:
            await self.update_files_list()

            remote_url = self.base_url + file_path
            local_path = os.path.join(os.getcwd(), file_path)

            if file_path not in self.repository_files:
                local_path = os.path.join(os.getcwd(), file_path)
                print(f"Deleting file: {local_path}")
                os.remove(local_path)

            else:
                if not os.path.exists(local_path):
                    await self.download_file(remote_url, local_path)
                else:
                    await self.update_file_if_needed(remote_url, local_path)

        await self.close_session()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HayesUB Updater.")
    parser.add_argument("--check", action="store_true", help="Check files for relevance")
    args = parser.parse_args()

    updater = Updater()
    if args.check:
        asyncio.run(updater.check_files())
    else:
        asyncio.run(updater.update_all_files())
