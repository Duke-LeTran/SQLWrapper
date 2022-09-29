import logging
import sqlalchemy

from sqlwrapper.base import SQL
from sqlwrapper.config import PATH_TO_CONFIG, CONFIG_FILE
from sqlwrapper.dbmenu import db_menu

log = logging.getLogger(__name__)

class MariaDB(SQL): # level 1
    """
    MariaDB Database Wrapper
    Things to note in Oracle:
        * schemas == users
        * hostname == server
        * service_name == nickname of tnsaora file`
    This assumse you have all your Oracle ENV variables set correctly, e.g.

    """
    def __init__(self, config='redcap', opt_print=False): #defaults to Velos
        config = db_menu(PATH_TO_CONFIG, CONFIG_FILE, opt_print=opt_print).read_config(db=config) # local variable not saved
        super(MariaDB, self).__init__(schema_name=config['hello']) # username is schema
        self._generate_engine(config)
        self._generate_inspector
        self._save_config(config)

    def __del__(self):
        try:
            self.engine.dispose()
        except AttributeError: # never successfully made an engine
            pass
        try:
            self.conn.close()
        except AttributeError: #never sucessfully made a connection :'(
            pass
    
    def _generate_engine(self, config):
        """ generate engine"""
         # A. generate using string method
        try:
            self.engine = sqlalchemy.create_engine(\
                f"mysql+pymysql://{config['hello']}:{config['world']}@{config['hostname']}:{config['port']}/{config['db_name']}")
        except Exception as error:
            log.error(error)
    
    def _generate_inspector(self):
        from sqlalchemy import inspect
        self.inspector = inspect(self.engine)