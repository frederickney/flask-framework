import os, logging
import Server
from Database import Database
from Config import Environment
os.environ.setdefault("log_file", os.environ.get("LOG_FILE", "/var/log/server/process.log"))
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s]: %(message)s',
    filename=os.environ.get('log_file')
)
logging.info("Starting server...")
logging.info("Loading configuration file...")
if 'CONFIG_FILE' in os.environ:
    Environment.load(os.environ['CONFIG_FILE'])
else:
    Environment.load("/etc/server/config.json")
logging.info("Configuration file loaded...")
logging.basicConfig()
logging.getLogger().setLevel(Environment.SERVER_DATA['LOG_LEVEL'].upper()),
logging.debug("Connecting to default database...")
Database.register_engines(Environment.SERVER_DATA['LOG_LEVEL'] == 'debug')
Database.init()
logging.debug("Default database connected...")
Server.Process.init(tracking_mode=False)
# Server.Process.init_sheduler()
logging.debug("Server initialized...")
logging.debug("Loading server routes...")
Server.Process.load_routes()
Server.Process.load_middleware()
Server.Process.load_socket_events()
logging.debug("Server routes loaded...")
# app.teardown_appcontext(Database.save)
logging.info("Server is now starting...")
import Extensions
Extensions.load()
app = Server.Process.instanciate()

if __name__ == '__main__':
    app.run()