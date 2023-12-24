from logger import Moon, LogLevel

from pathlib import Path
from typing import Any, List

import os
import ast
import zipfile
import pyfiglet
import asyncio
import aiofiles
import datetime
import configparser


class Utils:
    class ClassFinder(ast.NodeVisitor):
        def __init__(self):
            self.class_name = None
            self.found: bool = False

        def visit_ClassDef(self, node):
            if node.name == self.class_name:
                self.found = True

        async def find_class_in_file(self, file_path: str) -> bool:
            try:
                async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    tree = ast.parse(await file.read(), filename=file_path)

            except SyntaxError as e:
                Utils.base_logger.error(e)
                return False

            finder = Utils.ClassFinder()
            finder.class_name = self.class_name
            finder.visit(tree)
            return finder.found

        def find_class_by_id(self, class_id: int, base_folder: str = "."):
            self.class_name = class_id
            for root, dirs, files in os.walk(base_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path.endswith(('.py', '.pyc')):
                        if self.find_class_in_file(file_path):
                            return file_path

            return None

    class Files:
        @staticmethod
        def log_path(filename: str) -> str:
            if filename:
                os.makedirs('logs', exist_ok=True)
                return os.path.join('logs', filename)
            else:
                return 'logs'

        @classmethod
        def join_paths(cls, *paths: str):
            return Path(*paths)

        @classmethod
        def get_parent_directory(cls, path_str: str) -> Path:
            return Path(path_str).parent

        @classmethod
        def get_file_name(cls, path_str: str) -> str:
            return Path(path_str).name

        @classmethod
        def is_absolute_path(cls, path_str: str) -> bool:
            return Path(path_str).is_absolute()

        @classmethod
        def file_exists(cls, path_str: str) -> bool:
            return Path(path_str).is_file()

        @classmethod
        def directory_exists(cls, path_str: str) -> bool:
            return Path(path_str).is_dir()

        @classmethod
        def create_directory(cls, path_str: str) -> Path:
            path = Path(path_str)
            path.mkdir(parents=True, exist_ok=True)
            return path

        @classmethod
        def list_files_in_directory(cls, path_str: str) -> list:
            return [str(file) for file in Path(path_str).iterdir() if file.is_file()]

        @classmethod
        def list_directories_in_directory(cls, path_str: str) -> list:
            return [str(directory) for directory in Path(path_str).iterdir() if directory.is_dir()]

        @classmethod
        async def read_text_file(cls, path_str: str) -> str:
            try:
                async with aiofiles.open(path_str, 'r') as file:
                    return await file.read()

            except Exception as e:
                Utils.base_logger.error(f"Error reading from file '{path_str}': {e}")
                return ''

        @staticmethod
        def get_all_files(folder_path):
            files = []
            for filename in os.listdir(folder_path):
                filepath = os.path.join(folder_path, filename)
                if os.path.isfile(filepath):
                    files.append(filepath)
            return files

        @staticmethod
        async def archive_file(file_path, timestamp: bool = False, strftime: str = "%Y%m%d%H%M%S%f") -> str:
            timestamp_str = datetime.datetime.utcnow().strftime(strftime)
            archive_path = f"{file_path}-{timestamp_str}.zip" if timestamp else f"{file_path}.zip"

            async with aiofiles.open(file_path, 'rb') as file:
                content = await file.read()

            with zipfile.ZipFile(archive_path, 'w', compression=zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.writestr(os.path.basename(file_path), content)

            os.remove(file_path)
            return archive_path

        @staticmethod
        async def get_folder_size_async(folder_path: str) -> int:
            total_size = 0
            if os.name == 'nt':
                for dirpath, dirnames, filenames in os.walk(folder_path):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        async with aiofiles.open(filepath, 'rb') as file:
                            total_size += await file.stat().st_size()
            else:
                for dirpath, dirnames, filenames in os.walk(folder_path):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        stat = await asyncio.to_thread(os.stat, filepath)
                        total_size += stat.st_size
            return total_size

        @staticmethod
        async def archive_files(file_paths: List[str], strftime: str = "%Y%m%d%H%M%S%f") -> str:
            timestamp_str = datetime.datetime.utcnow().strftime(strftime)
            archive_path = f"cache-{timestamp_str}.zip"

            async def write_to_zip(zip_file):
                for file_path in file_paths:
                    async with aiofiles.open(file_path, 'rb') as file:
                        content = await file.read()
                        zip_file.writestr(os.path.basename(file_path), content)

            await asyncio.to_thread(
                lambda: zipfile.ZipFile(archive_path, 'w', compression=zipfile.ZIP_DEFLATED),
                write_to_zip
            )

            for file_path in file_paths:
                await os.remove(file_path)

            return archive_path

        @classmethod
        async def write_text_file(cls, path_str: str, content: str) -> int:
            try:
                async with aiofiles.open(path_str, 'w') as file:
                    return await file.write(content)

            except Exception as e:
                Utils.base_logger.error(f"Error writing to file '{path_str}': {e}")
                return 0

        @classmethod
        async def append_to_text_file(cls, path_str: str, content: str) -> int:
            try:
                async with aiofiles.open(path_str, 'a') as file:
                    return await file.write(content)

            except Exception as e:
                Utils.base_logger.error(f"Error appending to file '{path_str}': {e}")
                return 0

        @classmethod
        async def append_text_if_not_exists(cls, file_path: str, text_to_add: str):
            async with aiofiles.open(file_path, 'r') as file:
                file_content = await file.read()

                if text_to_add not in file_content:
                    async with aiofiles.open(file_path, 'a') as file_append:
                        return await file_append.write("\n" + text_to_add)
                else:
                    Utils.base_logger.error(f"Text '{text_to_add}' already exists in the file.")

        @classmethod
        async def remove_text(cls, file_path: str, text_to_remove: str):
            async with aiofiles.open(file_path, 'r') as file:
                file_content = await file.read()

            if text_to_remove in file_content:
                file_content = file_content.replace(text_to_remove, '')

                async with aiofiles.open(file_path, 'w') as file_write:
                    await file_write.write(file_content)
            else:
                Utils.base_logger.warning(f"Text '{text_to_remove}' not found in the file: {file_path}")

        @staticmethod
        async def read_file(file_path):
            try:
                async with aiofiles.open(file_path, mode='rb') as file:
                    content = await file.read()
                    return content
            except FileNotFoundError as ex:
                Utils.base_logger.error(ex)

        @staticmethod
        async def save_content_to_file(content: str, file_path: str) -> bool:
            try:
                async with aiofiles.open(file_path, mode='wb') as file:
                    await file.write(content)
                return True
            except IOError as e:
                Utils.base_logger.error(f"Error saving content to file: {e}")
                return False

        @classmethod
        async def delete_file_async(cls, path_str: str) -> bool:
            async def delete_file():
                path = Path(path_str)
                if path.is_file():
                    path.unlink()
                    return True
                return False

            return await asyncio.to_thread(delete_file)

        @classmethod
        def delete_directory(cls, path_str: str) -> bool:
            path = Path(path_str)
            if path.is_dir():
                path.rmdir()
                return True
            return False

        @classmethod
        def copy_file(cls, source_path: str, destination_path: str) -> None:
            source = Path(source_path)
            destination = Path(destination_path)
            destination.write_text(source.read_text())

        @classmethod
        def move_file(cls, source_path: str, destination_path: str) -> None:
            source = Path(source_path)
            destination = Path(destination_path)
            source.rename(destination)

        @classmethod
        def get_absolute_path(cls, path_str: str) -> Path:
            return Path(path_str).absolute()

        @classmethod
        def change_extension(cls, path_str: str, new_extension: str) -> Path:
            path = Path(path_str)
            return path.with_suffix(new_extension)

        @classmethod
        def is_hidden(cls, path_str: str) -> bool:
            return Path(path_str).name.startswith('.')

    class Dictionary:
        @classmethod
        def get_key_by_subkey(cls, dictionary: dict | list, subkey_value: Any):
            for key, value in dictionary.items():
                if isinstance(value, list) and subkey_value in value:
                    return key
                elif isinstance(value, dict):
                    nested_result = cls.get_key_by_subkey(value, subkey_value)
                    if nested_result is not None:
                        return nested_result

            return None

        @classmethod
        def get_keys_with_value(cls, my_dict: dict, target_value: Any) -> list:
            return [key for key, value in my_dict.items() if value == target_value]

        @classmethod
        def merge_dicts(cls, my_dict: dict, other_dict: dict) -> dict:
            my_dict.update(other_dict)
            return my_dict

        @classmethod
        def filter_by_keys(cls, my_dict: dict, keys_to_keep: list) -> dict:
            return {key: value for key, value in my_dict.items() if key in keys_to_keep}

        @classmethod
        def reverse_items(cls, my_dict: dict) -> dict:
            return {value: key for key, value in my_dict.items()}

        @classmethod
        def multiply_values(cls, my_dict: dict, factor: Any) -> dict:
            return {key: value * factor for key, value in my_dict.items()}

        @classmethod
        def count_occurrences(cls, my_dict: dict, element: Any) -> int:
            return sum(1 for value in my_dict.values() if value == element)

        @classmethod
        def keys_by_value_range(cls, my_dict: dict, start: int, end: int) -> list:
            return [key for key, value in my_dict.items() if start <= value <= end]

        @classmethod
        def remove_empty_values(cls, my_dict: dict) -> dict:
            return {key: value for key, value in my_dict.items() if value}

        @classmethod
        def uppercase_keys(cls, my_dict: dict) -> dict:
            return {key.upper(): value for key, value in my_dict.items()}

        @classmethod
        def squared_values(cls, my_dict: dict) -> dict:
            return {key: value**2 for key, value in my_dict.items()}

        @classmethod
        def has_duplicate_values(cls, my_dict: dict) -> bool:
            seen = set()
            for value in my_dict.values():
                if value in seen:
                    return True
                seen.add(value)
            return False

        @classmethod
        def sum_values(cls, my_dict: dict) -> int:
            return sum(my_dict.values())

        @classmethod
        def filter_by_value_type(cls, my_dict: dict, value_type: Any) -> dict:
            return {key: value for key, value in my_dict.items() if isinstance(value, value_type)}

        @classmethod
        def invert_boolean_values(cls, my_dict: dict) -> dict:
            return {key: not value for key, value in my_dict.items() if isinstance(value, bool)}

        @classmethod
        def update_values(cls, my_dict: dict, update_func: Any) -> dict:
            return {key: update_func(value) for key, value in my_dict.items()}

    class Config:
        config: configparser.ConfigParser = configparser.ConfigParser()
        config_path = 'config.cfg'
        config.read(config_path)
        api_id: str = config.get('client', 'api_id')
        api_hash: str = config.get('client', 'api_hash')
        api_token: str = config.get('client', 'api_token')
        admin_id: str = config.get('client', 'admin_id')
        admin_ids: list = [admin_id]
        session_name: str = config.get('client', 'session_name')
        inline_session_name: str = config.get('client', 'inline_session_name')
        ipv6: bool = config.getboolean('args', 'ipv6')
        request_retries: int = config.getint('args', 'request_retries')
        retry_delay: int = config.getint('args', 'retry_delay')
        auto_reconnect: bool = config.getboolean('args', 'auto_reconnect')
        flood_sleep_threshold: int = config.getint('args', 'flood_sleep_threshold')
        device_model: str | None = config.get('args', 'device_model')
        system_version: str = config.get('args', 'system_version')
        app_version: str = config.get('args', 'app_version')
        lang_code: str = config.get('args', 'lang_code')
        entity_cache_limit: int = config.getint('args', 'entity_cache_limit')
        modules_repo: str = config.get('git', 'modules')
        auto_update: bool = config.getboolean('git', 'auto_update')        
        ModuleActions: bool = config.getboolean('logging', 'module')
        LoaderActions: bool = config.getboolean('logging', 'loader')
        ClientActions: bool = config.getboolean('logging', 'client')
        UtilsActions: bool = config.getboolean('logging', 'utils')

        def getval(section: str, value: str) -> str:
            return Utils.Config.config.get(section, value)

        def get_config() -> configparser.ConfigParser:
            return Utils.Config.config

        def get_config_path() -> str:
            return Utils.Config.config_path

    class Banner:
        @staticmethod
        def figlet(font: str = 'slant'):
            return pyfiglet.Figlet(font=font)

        @staticmethod
        def get(text, font: str = 'slant'):
            return Utils.Banner.figlet(font=font).renderText(text)

        @staticmethod
        def show(text, font: str = 'slant'):
            print(Utils.Banner.get(text, font=font))

    base_logger: Moon = Moon(
        name='Utils',
        log_file=Files.log_path('hayes.log'),
        stream_handler=False,
        file_handler=True,
        disabled=not Config.UtilsActions,
        file_level=LogLevel.DEBUG
    )
