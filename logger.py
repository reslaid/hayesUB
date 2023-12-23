import datetime
import json
import yaml
import logging
import os
import zipfile
import aiofiles
from enum import IntEnum
from prettytable import PrettyTable
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

class LogLevel(IntEnum):
    NOTSET = 0
    DEBUG = 10
    INFO = 20
    WARNING = 30
    WARN = WARNING
    ERROR = 40
    FATAL = 50
    CRITICAL = FATAL

class Moon:
    class Presets:
        class CLang(logging.Formatter):
            def format(self, record):
                levelname = record.levelname
                filename = record.filename
                lineno = record.lineno
                message = record.getMessage()

                if record.levelno == logging.DEBUG:
                    levelname = 'D'
                elif record.levelno == logging.INFO:
                    levelname = 'I'
                elif record.levelno == logging.WARNING:
                    levelname = 'W'
                elif record.levelno == logging.ERROR:
                    levelname = 'E'
                elif record.levelno == logging.CRITICAL:
                    levelname = 'F'

                return f"{filename}:{lineno}: {levelname}: {message}"

        class Json(logging.Formatter):
            def format(self, record):
                log_data = {
                    'timestamp': datetime.datetime.utcnow().isoformat(),
                    'level': record.levelname,
                    'message': record.getMessage()
                }
                return json.dumps(log_data)

        class Csv(logging.Formatter):
            def format(self, record):
                log_data = {
                    'timestamp': datetime.datetime.utcnow().isoformat(),
                    'level': record.levelname,
                    'message': record.getMessage()
                }
                return ','.join(log_data.values())

        class Table(logging.Formatter):
            def format(self, record):
                log_data = {
                    'timestamp': datetime.datetime.utcnow().isoformat(),
                    'level': record.levelname,
                    'message': record.getMessage()
                }

                table = PrettyTable()
                table.field_names = log_data.keys()
                table.add_row(log_data.values())

                return str(table)

        class Html(logging.Formatter):
            def format(self, record):
                log_data = {
                    'timestamp': datetime.datetime.utcnow().isoformat(),
                    'level': record.levelname,
                    'message': record.getMessage()
                }

                html_log = f"<p>{', '.join(f'<strong>{k}:</strong> {v}' for k, v in log_data.items())}</p>"
                return html_log

        class Xml(logging.Formatter):
            def format(self, record):
                log_data = {
                    'timestamp': datetime.datetime.utcnow().isoformat(),
                    'level': record.levelname,
                    'message': record.getMessage()
                }

                root = Element('log')
                for key, value in log_data.items():
                    SubElement(root, key).text = str(value)

                return minidom.parseString(tostring(root)).toprettyxml(indent="  ")

        class Markdown(logging.Formatter):
            def format(self, record):
                log_data = {
                    'timestamp': datetime.datetime.utcnow().isoformat(),
                    'level': record.levelname,
                    'message': record.getMessage()
                }

                markdown_log = '\n'.join([f"**{k}:** {v}" for k, v in log_data.items()])
                return markdown_log

        class Yaml(logging.Formatter):
            def format(self, record):
                log_data = {
                    'timestamp': datetime.datetime.utcnow().isoformat(),
                    'level': record.levelname,
                    'message': record.getMessage()
                }
                return yaml.dump(log_data, default_flow_style=False)

        class Syslog(logging.Formatter):
            def format(self, record):
                log_data = {
                    'timestamp': datetime.datetime.utcnow().isoformat(),
                    'level': record.levelname,
                    'message': record.getMessage()
                }
                return f"{log_data['timestamp']} {log_data['level']} {log_data['message']}"

        class JsonIndented(logging.Formatter):
            def format(self, record):
                log_data = {
                    'timestamp': datetime.datetime.utcnow().isoformat(),
                    'level': record.levelname,
                    'message': record.getMessage()
                }
                return json.dumps(log_data, indent=2)

        class Logstash(logging.Formatter):
            def format(self, record):
                log_data = {
                    '@timestamp': datetime.datetime.utcnow().isoformat(),
                    'loglevel': record.levelname,
                    'message': record.getMessage(),
                    'logger_name': record.name,
                    'path': record.pathname,
                    'line_number': record.lineno
                }
                return json.dumps(log_data)

        class SimpleHtml(logging.Formatter):
            def format(self, record):
                log_data = {
                    'timestamp': datetime.datetime.utcnow().isoformat(),
                    'level': record.levelname,
                    'message': record.getMessage()
                }

                html_log = f"<p><strong>Timestamp:</strong> {log_data['timestamp']}<br>"
                html_log += f"<strong>Level:</strong> {log_data['level']}<br>"
                html_log += f"<strong>Message:</strong> {log_data['message']}</p>"

                return html_log

        class ShortJson(logging.Formatter):
            def format(self, record):
                log_data = {
                    'timestamp': datetime.datetime.utcnow().isoformat(),
                    'level': record.levelname,
                    'message': record.getMessage()
                }
                return json.dumps(log_data, separators=(',', ':'))

        class ColoredConsole(logging.Formatter):
            COLORS = {
                'INFO': '\033[92m',  # Green
                'WARNING': '\033[93m',  # Yellow
                'ERROR': '\033[91m'  # Red
            }
            RESET = '\033[0m'

            def format(self, record):
                log_message = super().format(record)
                return f"{self.COLORS.get(record.levelname, '')}{log_message}{self.RESET}"

        class DelimiterSeparatedJson(logging.Formatter):
            def format(self, record):
                log_data = {
                    'timestamp': datetime.datetime.utcnow().isoformat(),
                    'level': record.levelname,
                    'message': record.getMessage()
                }
                return json.dumps(log_data, separators=(',', ':'))

    def __init__(self, name=__name__, log_file='logger.log', stream_handler: bool = True, file_handler: bool = True, disabled: bool = False, zipsize: int | None = 1024, stream_level: int = LogLevel.DEBUG, file_level: int = LogLevel.DEBUG):
        self.name = name
        self.log_file = log_file
        self.zipsize = zipsize
        self.file_level = file_level
        self.stream_level = stream_level

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level=self.stream_level)
        self.logger.disabled = disabled

        self.default_formatter = logging.Formatter("[{name}] [{asctime}] - [{levelname}]: {message}", style='{')

        self.add_stream_handler() if stream_handler else None
        self.add_file_handler() if file_handler else None

    def add_stream_handler(self):
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(self.stream_level)
        stream_handler.setFormatter(self.default_formatter)
        self.logger.addHandler(stream_handler)

    def add_file_handler(self, level=logging.DEBUG):
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(self.file_level)
        file_handler.setFormatter(self.default_formatter)
        self.logger.addHandler(file_handler)

    async def archive(self):
        archive_path = f"{self.log_file}.zip"

        async with aiofiles.open(self.log_file, 'rb') as file:
            async with aiofiles.open(archive_path, 'wb') as zipf:
                async with zipfile.ZipFile(zipf, 'w') as zip_file:
                    zip_file.writestr(os.path.basename(self.log_file), await file.read())

        os.remove(self.log_file)

        return self

    def set_log_format(self, log_format):
        self.default_formatter = logging.Formatter(log_format, style='{')

        for handler in self.logger.handlers:
            handler.setFormatter(self.default_formatter)

    def add_formatter(self, formatter):
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def del_formatters(self):
        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)

    def del_formatter(self, formatter):
        if formatter in self.logger.handlers:
            self.logger.removeHandler(formatter)

    def set_formatter(self, formatter):
        self.del_formatters()
        self.add_formatter(formatter=formatter)

    def debug(self, message, exc_info=None) -> None:
        self.logger.debug(message, exc_info=exc_info)

    def info(self, message, exc_info=None) -> None:
        self.logger.info(message, exc_info=exc_info)

    def warning(self, message, exc_info=None) -> None:
        self.logger.warning(message, exc_info=exc_info)

    def error(self, message, exc_info=None) -> None:
        self.logger.error(message, exc_info=exc_info)

    def critical(self, message, exc_info=None) -> None:
        self.logger.critical(message, exc_info=exc_info)

    def raise_message(self, exception_class, message) -> None:
        if issubclass(exception_class, BaseException):
            raise exception_class(message)

    def edit_format(self, new_log_format: str) -> None:
        required_placeholders = ["{message}"]
        if all(placeholder in new_log_format for placeholder in required_placeholders):
            self.set_log_format(new_log_format)
        else:
            self.error("Invalid log format")

    def reset_format(self) -> None:
        self.set_log_format(self.default_formatter)

    def base_logger(self) -> logging.Logger:
        return self.logger
