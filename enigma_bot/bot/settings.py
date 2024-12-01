from os import getenv, getcwd
from os.path import join
from datetime import datetime

from dotenv import load_dotenv

load_dotenv(override=True)

logs_path = join(getcwd(), 'logs')
log_file = join(logs_path, 'discord_{}.log'.format(datetime.now().strftime('%d_%m_%H_%M_%S')))

guild_id = int(getenv('DISCORD_GUILD_ID'))