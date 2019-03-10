# Copyright 2019 Michael J Simms
"""Entry point for bjoern WSGI"""

import argparse
import bjoern
import os
import signal
import sys
from start_flask import g_flask_app

def main():
    """Entry point for the bjoern-flask version of the app."""

    # Parse command line options.
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", default=False, help="Prevents the app from going into the background", required=False)
    parser.add_argument("--host", default="0.0.0.0", help="Host name on which users will access this website", required=False)
    parser.add_argument("--hostport", type=int, default=5000, help="Port on which users will access this website", required=False)
    parser.add_argument("--https", action="store_true", default=False, help="Runs the app as HTTPS", required=False)
    parser.add_argument("--num_workers", type=int, default=2, help="Maximum number of threads", required=False)

    try:
        args = parser.parse_args()
    except IOError as e:
        parser.error(e)
        sys.exit(1)

    bjoern.listen(g_flask_app, args.host, args.hostport)

    worker_pids = []

    for _ in xrange(args.num_workers):
        pid = os.fork()
        if pid > 0:
            worker_pids.append(pid)
        elif pid == 0:
            try:
                bjoern.run()
            except KeyboardInterrupt:
                pass
            exit()

    try:
        for _ in xrange(args.num_workers):
            os.wait()
    except KeyboardInterrupt:
        for pid in worker_pids:
            os.kill(pid, signal.SIGINT)

if __name__ == '__main__':
    main()
