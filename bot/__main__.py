"""Bot main module"""

from dotenv import load_dotenv
from extra.loggers import setup_logging

# load environmental variables
load_dotenv()

setup_logging()
