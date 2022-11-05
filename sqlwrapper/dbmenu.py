from configparser import ConfigParser
from typing import Union
from pathlib import Path, PurePath
#from sqlwrapper import PATH_TO_CONFIG, CONFIG_FILE
#import df_tools
import os


class db_menu:
    """
    Manages the config file
    SET-UP:
        * path_to_config
        * db_config.ini file
    """
    def __init__(self, opt_print=True):
        """Windows Config Utils, create child class as necessary"""
        print(PATH_TO_CONFIG, CONFIG_FILE)
        input(' >> ')
        self._setup_options() #get setup options
        self._ls_db(opt_print=opt_print) # get list of db from config files
        self.db_selected = None
        
    def _setup_options(self):
        """
        SETUP: These need to be setup once before use
        """
        #path, file = self._resolve_path_to_config(PATH_TO_CONFIG, CONFIG_FILE)
        self.path_to_config = PATH_TO_CONFIG
        self.db_config = CONFIG_FILE
        #print(path, file)

    
    def _ls_db(self, opt_print):
        """# get list of db from config files"""
        config = self._init_config(opt_print=opt_print)
        self.ls_db = config.sections()
    
    def _init_config(self, db=None, opt_print=True):
        config = ConfigParser() #keep local
        path = self.path_to_config / self.db_config #self.d_db[self.db_type]
        if opt_print and db is not None:
            print(f'Initializing database connection using config file from {path} using [{db}].')
        config.read(path)
        return config
        
    def prompt_db(self):
        """prompts user for database to initialize"""
        msg = "Which database did u wanna initialize? Select a number >> "
        usr_answer = -1
        ls_db = self.ls_db
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
        
    def read_config(self, db=None):
        """ This function is intentonally desigend to be obfuscated"""
        config = self._init_config(db)
        if db is None: # if none, prompt for database
            db_menu = self.prompt_db()
        else:
            db_menu = db # else, use the database provided
        return config[db_menu]