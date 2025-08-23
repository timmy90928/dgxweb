
#? sudo python3 app.py
#? sudo pip3 freeze > requirements.txt

from argparse import ArgumentParser
from enum import Enum

###* Register Blueprint ###
from application import create_app, APP

parser = ArgumentParser(
    prog = "dgxweb/app.py",
    description = "This program is a website of NVIDIA DGXS-V100 in the AI Lab.",
    epilog = "see the github: https://github.com/timmy90928/dgxweb"
)
group_mode = parser.add_mutually_exclusive_group()
group_mode.add_argument(
    "--mode",
    choices = ('development', 'production', 'testing'),
    help = "Select the execution mode."
)
group_mode.add_argument(
    "-m",
    choices = ('d', 'p', 't'),
    help = "Select the execution mode."
)
args = parser.parse_args()

class Mode(Enum):
    d = 'development'
    p = 'production'
    t = 'testing'

if args.mode:
    mode = args.mode
elif args.m:
    mode = Mode[args.m].value
else:
    mode = "production"

socketio = create_app(mode)
socketio.run(
    app = APP,
    host = "0.0.0.0",
    port = APP.config['PORT']
)