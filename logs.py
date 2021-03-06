# -*- coding: utf-8 -*-

from backoff import expo
from backoff import on_exception
from google.cloud import error_reporting
from google.cloud import logging
from logging import basicConfig
from logging import getLogger
from logging import NOTSET

# The format for local logs.
LOGS_FORMAT = ("%(asctime)s "
               "%(name)s "
               "%(process)d "
               "%(thread)d "
               "%(levelname)s "
               "%(message)s")

# The path to the log file for local logging.
LOG_FILE = "/tmp/trump2cash.log"


class Logs:
    """A helper for logging locally or in the cloud."""

    def __init__(self, name, to_cloud=True):
        self.to_cloud = to_cloud
        if self.to_cloud:
            # Use the Stackdriver logging and error reporting clients.
            self.logger = logging.Client().logger(name)
            self.error_client = error_reporting.Client()
        else:
            # Log to a local file.
            self.logger = getLogger(name)
            basicConfig(format=LOGS_FORMAT, level=NOTSET, filename=LOG_FILE)

    def debug(self, text):
        """Logs at the DEBUG level."""

        if self.to_cloud:
            self.safe_log_text(text, severity="DEBUG")
        else:
            self.logger.debug(text)

    def info(self, text):
        """Logs at the INFO level."""

        if self.to_cloud:
            self.safe_log_text(text, severity="INFO")
        else:
            self.logger.info(text)

    def warn(self, text):
        """Logs at the WARNING level."""

        if self.to_cloud:
            self.safe_log_text(text, severity="WARNING")
        else:
            self.logger.warning(text)

    def error(self, text):
        """Logs at the ERROR level."""

        if self.to_cloud:
            self.safe_log_text(text, severity="ERROR")
        else:
            self.logger.error(text)

    def catch(self, exception):
        """Logs an exception."""

        if self.to_cloud:
            self.safe_report_exception()
            self.safe_log_text(str(exception), severity="CRITICAL")
        else:
            self.logger.critical(str(exception))

    @on_exception(expo, BaseException, max_tries=5)
    def safe_log_text(self, text, severity):
        """Logs to the cloud and retries up to 5 times with exponential backoff
        if the upload fails.
        """

        self.logger.log_text(text, severity=severity)

    @on_exception(expo, BaseException, max_tries=5)
    def safe_report_exception(self):
        """Reports the latest exception to the cloud and retries up to 5 times
        with exponential backoff if the upload fails.
        """

        self.error_client.report_exception()
