from typing import Union
from pathlib import Path, PurePath
from sqlwrapper.config import config_reader
from sqlwrapper.oracle import Oracle
from sqlwrapper.sqlserver import SQLServer 
from sqlwrapper.mariadb import MariaDB 
import logging
#import df_tools
import os

log = logging.getLogger(__name__)
# class config_reader:
#     """
#     Manages the config file
#     SET-UP:
#         * PATH
#         * db_config.ini file
#     """
#     def __init__(self, opt_print=True):
#         """Windows Config Utils, create child class as necessary"""
#         self._init_config_path() #get setup options
#         self.db_selected = None
        
#     def _init_config_path(self):
#         """
#         SETUP: These need to be setup once before use
#         """
#         self.config_looker = c
#         self.PATH, self.FILE = self.config_looker.current
#         self.CONFIG = self.PATH / self.FILE

#     def read_config(self, db=None, opt_print=True):
#         config = ConfigParser() #keep local
#         path = self.PATH / self.FILE 
#         if opt_print and db is not None:
#             print(f'Initializing database connection using config file from {path} using [{db}].')
#         config.read(path)
#         return config
        

        
#     def read_config(self, db=None):
#         """ This function is intentonally desigend to be obfuscated"""
#         config = self._init_config(db)
#         if db is None: # if none, prompt for database
#             db_menu = self._prompt_db_entry()
#         else:
#             db_menu = db # else, use the database provided
#         return config[db_menu]

def connect(db_entry:str=None):
    menu = db_menu()
    db = menu.connect(db_entry)
    return db
    

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
            'mariadb' : MariaDB
        }
    
    def append_path(self, path):
        self._config_reader.append_path(path)
    
    def read_config(self, *args, **kwargs):
        return self._config_reader.read(*args, **kwargs)
    
    def switch_config(self):
        self._config_reader.select_config()


    def connect(self, db_entry:str=None):
        if db_entry is None:
            db_entry = self._prompt_db_entry()
        
        db_section = self.read_config(db_entry, opt_print=False)
        try:
            db_type=db_section['db_type'].lower()
            Database = self.map_Database[db_type]
            return Database(db_entry)
        except KeyError as e:
            log.traceback(' Traceback '.center(80, '-'))
            log.warning("No `db_type` specified in entry.")
            return None
        
    
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
                return None
            if usr_answer in range(len(ls_db)): #if correct answer.
                return ls_db[usr_answer]
            else: # repeat if error
                print("Number not in list. Exiting. Try again.")
                break
