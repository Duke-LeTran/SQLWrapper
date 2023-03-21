from typing import Union
from pathlib import Path, PurePath
from sqlwrapper.config import config_reader
from sqlwrapper.oracle import Oracle
from sqlwrapper.sqlserver import SQLServer 
from sqlwrapper.mariadb import MariaDB 
from dotenv import load_dotenv
from pathlib import Path
import hvac
import logging
from configparser import InterpolationSyntaxError, SectionProxy
#import df_tools
import sys
import os
import traceback

log = logging.getLogger(__name__)

################################################################################
# DB_MENU
################################################################################
class Database:
    """generic database for ocnnecting to the types available"""
    def __init__(self, db_entry:str, db_section:SectionProxy):
        self.db_entry=db_entry,
        self.db_section=db_section,
        self.db_type=db_section['db_type'].lower()

    @property
    def map_Database(self):
        return {
            'oracle' : Oracle,
            'sqlserver' : SQLServer,
            'mariadb' : MariaDB,
            'mysql' : MariaDB
        }
    
    def connect(self):
        """returns the db object"""
        self.map_Database[self.db_entry]
        Database = self.map_Database[self.db_type]
        return Database(self.db_entry, db_section=self.db_section)
    
    
class db_menu:
    def __init__(self):
        self._config_reader = config_reader()
    
    @property
    def config(self):
        return self._config_reader.config

    @property
    def current(self) -> None:
        print('-'*50)
        print(self._config_reader.df_config)
        print('-'*50)
        print('  > Current config:', self._config_reader._CONFIG)
        print('  > Use menu.select_config() to switch.')
        #return self._CONFIG

    @property
    def entries(self):
        return self._config_reader.entries
    
    @property
    def path(self):
        return self._config_reader.config_path
    
    @property
    def df_config(self):
        return self._config_reader.df_config
    
    @property
    def map_Database(self):
        return {
            'oracle' : Oracle,
            'sqlserver' : SQLServer,
            'mariadb' : MariaDB,
            'mysql' : MariaDB
        }
    
    def append_path(self, path):
        self._config_reader.append_path(path)
    
    def read_config(self, *args, **kwargs):
        """This is a proxy function to the CONFIG_READER object"""
        return self._config_reader.read(*args, **kwargs)


    def switch_config(self):
        self._config_reader.select_config()


    def connect(self, 
                db_entry:str=None,
                interpolate=False,
                sec_path:str=None,
                map_secrets:dict=None):
        # if using vault
        if sec_path is not None:
            if db_entry is None:
                db_entry = sec_path.split('/')[-1]
            db_section = self.read_config(sec_path=sec_path, 
                                          map_secrets=map_secrets, 
                                          db_entry=db_entry,
                                          vault=True)
            #return db_section
            return self._connect(db_entry, db_section)
        # else, connect via menu or by db_entry
        else:
            # via menu
            if db_entry is None:
                db_entry = self._prompt_db_entry()
                if db_entry == 0: # Exit, per use request
                    print('Exiting menu...')
                    return
                # if db_entry is False: #
                #     return
            
            # directly via db_entry
            db_section = self.read_config(db_entry, 
                                      opt_print=False,
                                      interpolate=interpolate)
            return self._connect(db_entry, db_section)
        
    
    def _connect(self, db_entry:str, db_section:SectionProxy):
        
        try:
            db_type=db_section['db_type'].lower()
            Database = self.map_Database[db_type]
            return Database(db_entry, db_section=db_section)
        except KeyError as e:
            log.error(e,  exc_info=True)
            #log.traceback(' Traceback '.center(80, '-'))
            exc_type, exc_value, exc_traceback = sys.exc_info()
            log.info(' exc_info '.center(80, '-'))
            log.info(exc_type, exc_value, exc_traceback)
            traceback_in_var = traceback.format_tb(exc_traceback)
            log.info(' traceback_in_var '.center(80, '-'))
            log.info(traceback_in_var)
            log.warning("No `db_type` specified in entry.")
            return None
        except Exception as e:
            log.error(e, exc_info=True)
        
    
    def _prompt_db_entry(self):
        """prompts user for database to initialize"""
        msg = "Which database did u wanna initialize? Select a number >> "
        usr_answer = -1
        ls_db = self.entries
        ls_db.insert(0,'Exit.')
        while usr_answer < 0:
            try:
                print("MENU\n-----")
                for i, db in enumerate(ls_db):
                    print(i, db)
                usr_answer = int(input(msg))
            except ValueError: # if user 
                print("I said number bro, specifically, an integer.")
                continue
            if usr_answer == 0: # if user wants to exit prompt.
                return 0
                #return None
            if usr_answer in range(len(ls_db)): #if correct answer.
                return ls_db[usr_answer]
            else: # repeat if error
                print("Number not in list. Exiting. Try again.")
                break
