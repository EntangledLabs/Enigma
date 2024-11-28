import tomllib
from os import getenv

from dotenv import load_dotenv

from os import getcwd

load_dotenv()

db_url = getenv('DB_URL')
discord_api_key = getenv('DISCORD_API_KEY')

boxes_path = './boxes/'                     # Path to boxes config directory
creds_path = './creds/'                     # Path to creds config directory
logs_path = './logs/'                       # Path to logs config directory
injects_path = './injects/'                 # Path to injects config directory
test_artifacts_path = './test_artifacts/'   # Path to test artifacts directory (only used for testing)
scores_path = './scores/'                   # Path to scores directory

not_found_response = {404: {'description': 'Not found'}}