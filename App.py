# Copyright 2019 Michael J Simms
"""Main application, contains all web page handlers"""

import datetime
import json
import logging
import mako
import markdown
import os
import Api

from dateutil.tz import tzlocal
from mako.lookup import TemplateLookup
from mako.template import Template


PRODUCT_NAME = 'RunEverywhere'
DEFAULT_LOGGED_IN_URL = '/index'
HTML_DIR = 'html'


class RedirectException(Exception):
    """This is thrown when the app needs to redirect to another page."""

    def __init__(self, url):
        self.url = url
        super(RedirectException, self).__init__()


class App(object):
    """Class containing the URL handlers."""

    def __init__(self, root_dir, root_url):
        self.root_dir = root_dir
        self.root_url = root_url
        self.tempfile_dir = os.path.join(self.root_dir, 'tempfile')
        self.tempmod_dir = os.path.join(self.root_dir, 'tempmod')
        self.tempfile_dir = os.path.join(root_dir, 'tempfile')
        if not os.path.exists(self.tempfile_dir):
            os.makedirs(self.tempfile_dir)

        super(App, self).__init__()

    def log_error(self, log_str):
        """Writes an error message to the log file."""
        logger = logging.getLogger()
        logger.error(log_str)

    def index(self):
        """Renders the index page."""
        html_file = os.path.join(self.root_dir, HTML_DIR, 'index.html')
        my_template = Template(filename=html_file, module_directory=self.tempmod_dir)
        return my_template.render(product=PRODUCT_NAME, root_url=self.root_url)

    def api(self, user_id, method, params):
        """Handles an API request."""
        api = Api.Api(self.tempfile_dir, user_id, self.root_url)
        handled, response = api.handle_api_1_0_request(method, params)
        return handled, response
