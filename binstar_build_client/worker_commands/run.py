'''
Build worker
'''

from __future__ import (print_function, unicode_literals, division,
    absolute_import)

import logging
import os
import yaml

from binstar_client.utils import get_binstar

from binstar_build_client import BinstarBuildAPI
from binstar_build_client.utils import get_conda_root_prefix
from binstar_build_client.worker.worker import Worker
from binstar_build_client.worker.register import WorkerConfiguration


log = logging.getLogger('binstar.build')



def main(args):
    worker_config = WorkerConfiguration.load(args.worker_id)

    log.info(str(worker_config))

    bs = get_binstar(args, cls=BinstarBuildAPI)

    worker = Worker(bs, worker_config, args)

    worker.write_status(True, "Starting")

    try:
        with worker_config.running():
            worker.work_forever()
    finally:
        worker.write_status(False, "Exited")

def add_worker_dev_options(parser):

    dgroup = parser.add_argument_group('development options')

    dgroup.add_argument("--conda-build-dir",
                        default=os.path.join(get_conda_root_prefix(),
                                             'conda-bld', '{args.platform}'),
                        help="[Advanced] The conda build directory (default: %(default)s)",
                        )

    dgroup.add_argument('--show-new-procs', action='store_true', dest='show_new_procs',
                        help='Print any process that started during the build '
                             'and is still running after the build finished')

    dgroup.add_argument('--status-file',
                        help='If given, binstar will update this file with the ' + \
                             'time it last checked the anaconda server for updates')

    parser.add_argument('--cwd', default=os.path.abspath('.'), type=os.path.abspath,
                        help='The root directory this build should use (default: "%(default)s")')

    parser.add_argument('-t', '--max-job-duration', type=int, metavar='SECONDS',
                        dest='timeout',
                        help='Force jobs to stop after they exceed duration (default: %(default)s)', default=60 * 60)
    return parser

def add_parser(subparsers, name='run',
               description='Run a build worker to build jobs off of a binstar build queue',
               epilog=__doc__,
               default_func=main):

    parser = subparsers.add_parser(name,
                                   help=description, description=description,
                                   epilog=epilog
                                   )
    parser.add_argument('worker_id',
                        help="worker_id that was given in anaconda build register")
    parser.add_argument('-f', '--fail', action='store_true',
                        help='Exit main loop on any un-handled exception')
    parser.add_argument('-1', '--one', action='store_true',
                        help='Exit main loop after only one build')
    parser.add_argument('--push-back', action='store_true',
                        help='Developers only, always push the build *back* ' + \
                             'onto the build queue')

    parser = add_worker_dev_options(parser)
    parser.set_defaults(main=default_func)
    return parser