# Copyright 2019 Michael J Simms
"""API request handlers"""

import json
import logging
import os
import time
import urllib


class Api(object):
    """Class for managing API messages."""

    def __init__(self, temp_dir, user_id, root_url):
        super(Api, self).__init__()
        self.temp_dir = temp_dir
        self.user_id = user_id
        self.root_url = root_url

    def log_error(self, log_str):
        """Writes an error message to the log file."""
        logger = logging.getLogger()
        logger.debug(log_str)

    def handle_api_1_0_request(self, request, values):
        """Called to parse a version 1.0 API message."""
        return False, ""
