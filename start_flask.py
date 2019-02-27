# Copyright 2019 Michael J Simms
"""Main application, contains all web page handlers"""

import argparse
import logging
import mako
import os
import signal
import sys
import traceback
import flask

import Api
import App


CSS_DIR = 'css'
JS_DIR = 'js'
IMAGES_DIR = 'images'
ERROR_LOG = 'error.log'


g_backend = None
g_flask_app = flask.Flask(__name__)
g_flask_app.secret_key = '13auWH9ZtH1n5Kh7rnE9'
g_flask_app.url_map.strict_slashes = False


def signal_handler(signal, frame):
    print("Exiting...")
    sys.exit(0)

@g_flask_app.route('/css/<file_name>')
def css(file_name):
    """Returns the CSS page."""
    try:
        return flask.send_from_directory(CSS_DIR, file_name)
    except:
        g_backend.log_error(traceback.format_exc())
        g_backend.log_error(sys.exc_info()[0])
        g_backend.log_error('Unhandled exception in ' + css.__name__)
    return g_backend.error()

@g_flask_app.route('/js/<file_name>')
def js(file_name):
    """Returns the JS page."""
    try:
        return flask.send_from_directory(JS_DIR, file_name)
    except:
        g_backend.log_error(traceback.format_exc())
        g_backend.log_error(sys.exc_info()[0])
        g_backend.log_error('Unhandled exception in ' + js.__name__)
    return g_backend.error()

@g_flask_app.route('/images/<file_name>')
def images(file_name):
    """Returns images."""
    try:
        return flask.send_from_directory(IMAGES_DIR, file_name)
    except:
        g_backend.log_error(traceback.format_exc())
        g_backend.log_error(sys.exc_info()[0])
        g_backend.log_error('Unhandled exception in ' + images.__name__)
    return g_backend.error()

@g_flask_app.route('/api/<version>/<method>', methods = ['GET','POST'])
def api(version, method):
    """Endpoint for API calls."""
    response = ""
    code = 200
    try:
        # Get the logged in user.
        user_id = None
        username = g_backend.user_mgr.get_logged_in_user()
        if username is not None:
            user_id, _, _ = g_backend.user_mgr.retrieve_user(username)

        # The the API params.
        if flask.request.method == 'GET':
            params = ""
        else:
            params = json.loads(flask.request.data)

        # Process the API request.
        if version == '1.0':
            handled, response = g_backend.api(user_id, method, params)
            if not handled:
                response = "Failed to handle request: " + str(method)
                g_backend.log_error(response)
                code = 400
            else:
                code = 200
        else:
            g_backend.log_error("Failed to handle request for api version " + version)
            code = 400
    except Exception as e:
        response = str(e.args[0])
        g_backend.log_error(response)
        code = 500
    except:
        code = 500
    return response, code

@g_flask_app.route('/')
def index():
    """Renders the index page."""
    result = ""
    try:
        result = g_backend.index()
    except:
        result = g_backend.error()
    return result

def main():
    """Entry point for the flask version of the app."""
    global g_backend

    # Parse command line options.
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", default=False, help="Prevents the app from going into the background", required=False)
    parser.add_argument("--host", default="", help="Host name on which users will access this website", required=False)
    parser.add_argument("--hostport", type=int, default=5000, help="Port on which users will access this website", required=False)
    parser.add_argument("--https", action="store_true", default=False, help="Runs the app as HTTPS", required=False)

    try:
        args = parser.parse_args()
    except IOError as e:
        parser.error(e)
        sys.exit(1)

    if args.https:
        protocol = "https"
    else:
        protocol = "http"

    if len(args.host) == 0:
        if args.debug:
            args.host = "127.0.0.1"
        else:
            args.host = "run-everywhere.com"
        print("Hostname not provided, will use " + args.host)

    root_url = protocol + "://" + args.host
    if args.hostport > 0:
        root_url = root_url + ":" + str(args.hostport)
    print("Root URL is " + root_url)

    signal.signal(signal.SIGINT, signal_handler)
    mako.collection_size = 100
    mako.directories = "templates"

    root_dir = os.path.dirname(os.path.abspath(__file__))
    g_backend = App.App(root_dir, root_url)

    logging.basicConfig(filename=ERROR_LOG, filemode='w', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    # The markdown library is kinda spammy.
    markdown_logger = logging.getLogger("MARKDOWN")
    markdown_logger.setLevel(logging.ERROR)

    g_flask_app.run(debug=args.debug)

if __name__ == '__main__':
    main()
