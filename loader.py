from logger import Moon, LogLevel
from utils import Utils

from typing import Any
from telethon import TelegramClient, events, Button
from datetime import datetime

import os
import telethon
import importlib
import importlib.util
import importlib.metadata
import sys
import subprocess
import re
import inspect
import py_compile
import ast
import functools
import types
import aiofiles
import aiohttp


class Module:
    _start_time: datetime = datetime.now()

    tl = telethon
    Btn = Button

    utils = Utils
    Utils = Utils

    _name: str = 'Unknown'
    _description: str = 'None'

    _results: list = []
    _commands: dict = {}
    _module_descriptions: dict = {}
    _module_filename: dict = {}

    events = events

    CallbackQuery: events.CallbackQuery = events.CallbackQuery
    InlineQuery: events.InlineQuery = events.InlineQuery

    client = TelegramClient(
        session=Utils.Config.session_name,
        api_id=Utils.Config.api_id,
        api_hash=Utils.Config.api_hash,
        use_ipv6=Utils.Config.ipv6,
        request_retries=Utils.Config.request_retries,
        retry_delay=Utils.Config.retry_delay,
        auto_reconnect=Utils.Config.auto_reconnect,
        flood_sleep_threshold=Utils.Config.flood_sleep_threshold,
        device_model=Utils.Config.device_model,
        system_version=Utils.Config.system_version,
        app_version=Utils.Config.app_version,
        lang_code=Utils.Config.lang_code,
        entity_cache_limit=Utils.Config.entity_cache_limit,
        base_logger=Moon(
            name=TelegramClient.__name__,
            log_file=Utils.Files.log_path('client.log'),
            disabled=not Utils.Config.ClientActions,
            stream_handler=False,
            file_level=LogLevel.INFO
        ).base_logger()
    )

    inline: TelegramClient = TelegramClient(
        session=Utils.Config.inline_session_name,
        api_id=Utils.Config.api_id,
        api_hash=Utils.Config.api_hash
    )

    @classmethod
    def init(cls):
        cls._name = cls.__name__
        cls._module_descriptions[cls._name] = cls.__doc__ if cls.__doc__ else 'None'

    @staticmethod
    async def get_me() -> telethon.types.User | telethon.types.InputPeerUser:
        return await Module.client.get_me()

    @staticmethod
    async def get_command(event) -> str:
        message_parts = event.message.text.split(' ')
        return message_parts[0]

    @staticmethod
    async def get_args(event, maxsplit=15) -> list | str:
        message_parts = event.message.text.split(' ', maxsplit=maxsplit)
        return message_parts[1:]

    @classmethod
    def get_logger(cls, name: str | None = None, filename: str | None = "module.log", formatter: Moon.Presets = Moon.Presets.Syslog()) -> Moon:
        logger: Moon = Moon(
            name=name or cls.__name__,
            log_file=Utils.Files.log_path(filename),
            disabled=not Utils.Config.ModuleActions,
            stream_handler=True,
            file_handler=True,
            stream_level=LogLevel.INFO,
            file_level=LogLevel.DEBUG,
        )
        logger.set_formatter(formatter)
        return logger

    @classmethod
    def req(cls, module_name: str, _importlib: bool = False) -> types.ModuleType:
        try:
            if not _importlib:
                return __import__(name=module_name, fromlist=[""])
            else:
                return importlib.import_module(module_name)
        except ImportError as ex:
            Loader.moon.error(ex)
            return None

    @classmethod
    def preq(cls, plugin_name: str, _importlib: bool = False) -> types.ModuleType:
        return cls.req(module_name=f"plugins.{plugin_name}", _importlib=_importlib)

    @staticmethod
    def add_command(cls, command: str, description: str = 'None', handler=None) -> None:
        if cls._name not in cls._commands:
            cls._commands[cls._name] = []
        cls._commands[cls._name].append({"command": f".{command}", "description": description, "handler": handler})

    @classmethod
    def remove_commands(cls, module_name: str) -> None:
        if module_name in cls._commands:
            del cls._commands[module_name]

    @classmethod
    def set_module_description(cls, description: str, module=None) -> None:
        if module is None:
            module = cls.__name__
        cls._module_descriptions[module] = description

    @classmethod
    def find_index_by_command(cls, module_name: str, command_name: str) -> int:
        for index, module in enumerate(cls._commands.get(module_name, [])):
            if module.get('command') == command_name:
                return index
        return -1

    @classmethod
    def update_command_description(cls, command_name: str, description: str) -> bool:
        index = cls.find_index_by_command(cls._name, command_name)
        if index != -1:
            cls._commands[cls._name][index]['description'] = description
            return True
        return False

    @classmethod
    def get_mdl_description(cls, module: str) -> Any:
        return cls._module_descriptions.get(module, 'None')

    @classmethod
    def module_list(cls) -> str:
        result: str = ""
        for module, commands in cls._commands.items():
            result += f'<b>🌒</b> <b><code>{module}</code>, filename: <code>{Utils.Dictionary.get_key_by_subkey(Loader.hooked_modules, module)}</code></b>\n'
        return result

    @classmethod
    def plugin_list(cls) -> str:
        result: str = ""
        valid_extensions = [".py", ".pyc"]

        for plugin in os.listdir('plugins'):
            if plugin == Loader.init_file:
                continue

            if any(plugin.lower().endswith(ext) for ext in valid_extensions):
                result += f'<b>🌒</b> <b><code>{Loader.get_module_name(plugin)}</code>, filename: <code>{plugin}</code></b>\n'

        return result

    @classmethod
    def module_commands(cls, module_name: str) -> str:
        result: str = ""

        if module_name in cls._commands:
            formatted_commands = [f'🌒<code>{command["command"]}</code>: <b>{command["description"]}</b>' for command in cls._commands[module_name]]
            result += '\n'.join(formatted_commands)
        else:
            result = 'None'

        return result

    @classmethod
    def module_commands_list(cls) -> str:
        result: str = ""
        for module, commands in cls._commands.items():
            formatted_commands = [f'<code>{command}</code>' for command in commands]
            result += f'<b>🌒</b> <b><code>{module}</code></b>: ({", ".join(formatted_commands)})\n'
        return result

    @classmethod
    def count_modules(cls) -> int:
        return len(cls._commands)

    @classmethod
    def count_plugins(cls) -> int:
        valid_extensions = [".py", ".pyc"]
        plugins = [file for file in os.listdir('plugins') if any(file.lower().endswith(ext) for ext in valid_extensions)]
        plugins.remove(Loader.init_file) if Loader.init_file in plugins else None
        return len(plugins)

    @staticmethod
    def restart() -> None:
        subprocess.Popen([sys.executable, sys.argv[0]])
        sys.exit()

    @staticmethod
    def exit() -> None:
        Module.client.disconnect()
        sys.exit()

    @staticmethod
    def uptime() -> str:
        return str(datetime.now() - Module._start_time)

    @classmethod
    def owner_command(cls, func):
        async def wrapper(event, pattern=None, **kwargs):
            if pattern:
                if event.raw_text and re.match(pattern, event.raw_text):
                    sender_id = event.sender.id if event.sender else event.from_id.user_id
                    if str(sender_id) not in Utils.Config.admin_ids:
                        return

                    if Utils.Dictionary.get_key_by_subkey(Loader.hooked_modules, cls._name) not in Loader.hooked_modules:
                        return

                    await func(event, **kwargs)

        async def event_handler(event):
            pattern = re.compile(r"\." + func.__name__)
            await wrapper(event, pattern=pattern)

        cls.client.add_event_handler(event_handler, events.NewMessage)
        cls.add_command(cls, command=func.__name__, description=func.__doc__ if func.__doc__ else 'None', handler=func)

        return wrapper

    @classmethod
    def command(cls, func):
        async def wrapper(event, pattern=None, **kwargs):
            if pattern:
                if event.raw_text and re.match(pattern, event.raw_text):
                    if Utils.Dictionary.get_key_by_subkey(Loader.hooked_modules, cls._name) not in Loader.hooked_modules:
                        return

                    await func(event, **kwargs)

        async def event_handler(event):
            pattern = re.compile(r"\." + func.__name__)
            await wrapper(event, pattern=pattern)

        cls.client.add_event_handler(event_handler, events.NewMessage)
        cls.add_command(cls, command=func.__name__, description=func.__doc__ if func.__doc__ else 'None', handler=func)

        return wrapper

    @classmethod
    def strict_owner_command(cls, func):
        async def wrapper(event, **kwargs):
            if event.raw_text and event.raw_text.split(' ')[0] == f".{func.__name__}":
                sender_id = event.sender.id if event.sender else event.from_id.user_id
                if str(sender_id) not in Utils.Config.admin_ids:
                    return

                if Utils.Dictionary.get_key_by_subkey(Loader.hooked_modules, cls._name) not in Loader.hooked_modules:
                    return

                await func(event, **kwargs)

        async def event_handler(event):
            await wrapper(event)

        cls.client.add_event_handler(event_handler, events.NewMessage)
        cls.add_command(cls, command=func.__name__, description=func.__doc__ if func.__doc__ else 'None', handler=func)

        return wrapper

    @classmethod
    def strict_command(cls, func):
        async def wrapper(event, **kwargs):
            if event.raw_text and event.raw_text.split(' ')[0] == f".{func.__name__}":
                if Utils.Dictionary.get_key_by_subkey(Loader.hooked_modules, cls._name) not in Loader.hooked_modules:
                    return

                await func(event, **kwargs)
            else:
                pass

        async def event_handler(event):
            await wrapper(event)

        cls.client.add_event_handler(event_handler, events.NewMessage)
        cls.add_command(cls, command=func.__name__, description=func.__doc__ if func.__doc__ else 'None', handler=func)

        return wrapper

    @classmethod
    def watcher(cls, func, chats=None):
        @cls.client.on(events.NewMessage(chats=chats))
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        return wrapper

    @classmethod
    def chat_action(cls, action):
        def decorator(func):
            @cls.client.on(events.ChatAction(func=action))
            async def wrapper(event):
                return await func(event)

            return wrapper

        return decorator

    @classmethod
    def inline_query(cls):
        def decorator(func):
            async def wrapper(*args, **kwargs):
                await func(*args, **kwargs)

            cls.inline.add_event_handler(wrapper, cls.InlineQuery())
            return wrapper

        return decorator

    @classmethod
    def callback_query(cls):
        def decorator(func):
            async def wrapper(*args, **kwargs):
                await func(*args, **kwargs)

            cls.inline.add_event_handler(wrapper, cls.CallbackQuery())
            return wrapper

        return decorator


class Loader:
    module_folder: str = "modules"
    plugin_folder: str = "plugins"
    logs_folder: str = "logs"
    pycache_folder: str = "__pycache__"
    init_file: str = "__init__.py"
    valid_extensions: list = [".py", ".pyc"]
    module_files = [file for file in os.listdir(module_folder) if file.endswith(".py")]
    compiled_module_files = [file for file in os.listdir(module_folder) if file.endswith(".pyc")]
    mode: str = "exec"
    moon: Moon = Moon(__name__, log_file=Utils.Files.log_path("hayes.log"), stream_handler=LogLevel.DEBUG, file_level=LogLevel.INFO)
    moon.base_logger().disabled = not Utils.Config.LoaderActions
    moon.set_formatter(moon.Presets.Syslog())
    moon_id: int = id(moon)
    loaded_modules: set = set()
    hooked_modules: dict = {}

    @staticmethod
    async def update_module_list() -> None:
        Loader.module_files = [file for file in os.listdir(Loader.module_folder) if file.endswith(".py")]
        Loader.compiled_module_files = [file for file in os.listdir(Loader.module_folder) if file.endswith(".pyc")]

    @staticmethod
    def check_extension(file_path: str, extension: str) -> bool:
        _, file_extension = os.path.splitext(file_path)
        return file_extension.lower() == extension.lower()

    @staticmethod
    def get_module(module_file: str) -> str:
        return os.path.join(Loader.module_folder, module_file)

    @staticmethod
    def get_python_module(module_file: str) -> str:
        return f"{Loader.module_folder}.{Loader.get_module_name(module_file)}"

    @staticmethod
    def get_module_name(module_file: str) -> str:
        return os.path.splitext(os.path.basename(module_file))[0]

    @staticmethod
    async def hook(code: str) -> None:
        exec(code)
        return None

    @staticmethod
    async def generate_raw_pastebin_url(pastebin_link: str) -> str:
        return f'https://pastebin.com/raw/{pastebin_link}'

    @staticmethod
    async def get_content(url: str) -> bytes | str:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        Loader.moon.error(f"Failed to download file. Status code: {response.status}")
                        return None
            except aiohttp.ClientError as e:
                Loader.moon.error(f"Failed to download file. Error: {e}")
                return None

    @staticmethod
    async def compile_module(module_file: str, _optimize: int = -1) -> None:
        compiled_file = f"{Loader.get_module_name(module_file)}.pyc"
        compiled_filepath = os.path.join(os.path.dirname(module_file), compiled_file)
        py_compile.compile(module_file, cfile=compiled_filepath, optimize=_optimize)

    @staticmethod
    async def get_module_classes(module_file_path: str) -> Any:
        module_name = Loader.get_module_name(module_file_path)

        try:
            async with aiofiles.open(module_file_path, mode='r', encoding='utf-8', errors='ignore') as file:
                file_content = await file.read()
                tree = ast.parse(file_content, filename=module_file_path)

            return [
                node.name
                for node in ast.walk(tree)
                if isinstance(node, ast.ClassDef)
            ]

        except Exception as e:
            Loader.moon.error(f"Error getting classes from '{module_name}': {e}")
            return []

    @staticmethod
    async def hook_module(module_file: str) -> None:
        await Loader.update_module_list()

        if module_file in Loader.hooked_modules:
            Loader.moon.debug(f"Module '{module_file}' already loaded. Skipping hooking.")
            return

        module_path = Loader.get_module(module_file)
        module_name: str = Loader.get_module_name(module_file)

        try:

            spec = importlib.util.spec_from_file_location(module_path, Loader.get_module(module_file=module_file))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            Loader.hooked_modules[module_file] = [name for name, obj in inspect.getmembers(module) if inspect.isclass(obj)]

            Loader.moon.debug(f"Module '{module_name}' Hooked.")
            Loader.loaded_modules.add(module_name)

        except Exception as e:
            Loader.moon.error(f"'{module_name}': {e}")

    @staticmethod
    async def hook_module_adv(module_file: str) -> None:
        await Loader.update_module_list()
        await Loader.hook_module(module_file=module_file)

    @staticmethod
    async def hook_modules() -> None:
        await Loader.update_module_list()

        for module_file in Loader.module_files:
            await Loader.hook_module(module_file=module_file)

        for compiled_module_file in Loader.compiled_module_files:
            await Loader.hook_module(module_file=compiled_module_file)

    @staticmethod
    async def unhook_module(module_name: str) -> None:
        if module_name not in Loader.hooked_modules:
            return

        for module in Loader.hooked_modules[module_name]:
            commands_to_remove = list(Module._commands.get(module, []))

            for command in commands_to_remove:
                handler_id = command.get("handler")
                if handler_id:
                    Module.client.remove_event_handler(handler_id)

            Module._commands.pop(module, None)

        Loader.hooked_modules.pop(module_name, None)
        Loader.moon.debug(f"Module '{module_name}' unhooked")
