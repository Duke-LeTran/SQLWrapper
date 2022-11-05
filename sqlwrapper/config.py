"""
SQLWrapper.py
    |--> db_menu.py
    |--> prompter.py
    
DESCRIPTION: 
    SQLWrapper object to help manage database connections on unix server. It
    features a config file similar to the Oracle tnsnames.ora

SETUP:
    1. Place and edit config files in ~/.mypylib/ 
    2. Run ```chmod 600 ~/.mypylib/db_config.ini``` to protect the files

Duke LeTran <duke.letran@gmail.com; daletran@ucdavis.edu>
Research Infrastructure, IT Health Informatics, UC Davis Health
"""
import os
import logging
from pathlib import Path, PurePath

# SQLWrapper
from sqlwrapper.dbmenu import db_menu
from sqlwrapper.prompter import Prompter
from typing import Union
# logging
log = logging.getLogger(__name__)

# setup
ls_path_to_config = [
    Path.home() / Path('.mypylib'),
    Path.cwd()
]

ls_config_file = [
    'db_config.ini', #name of your config file
    '.env',
    'config.env'
]

# prompter
p = Prompter()


class config_class:
    def __init__(self):
        # setup
        self.ls_path_to_config = ls_config_file
        self.ls_config_file = ls_config_file

    @property
    def init_config_path(self):
        return self._resolve_path_to_config(self.ls_path_to_config, self.ls_config_file)

    def _resolve_path_to_config(self, path_to_config:Union[list,Path, str], config_file:Union[list, str]):
        if type(path_to_config) == str:
            path_to_config = Path(path_to_config)
        if isinstance(path_to_config, PurePath): 
            if type(config_file) == list:
                for file in config_file:
                    if os.path.exists(path_to_config / file): # (PurePath, list)
                        return path_to_config, file
            else: # (PurePath, string)
                return path_to_config, config_file
        else:
            for path in path_to_config: 
                if type(config_file) == list: # (list, list)
                    for file in config_file:
                        config_file = Path(path) / file
                        if os.path.exists(config_file): # (list, list)
                            print(config_file)
                            return Path(path), file
                else: # (list, string)
                    return path, config_file

def ls(return_ls=False):
    """prints list of db in config file"""
    print("DATABASES\n-----")
    for i, db in enumerate(db_menu(PATH_TO_CONFIG, CONFIG_FILE).ls_db):
        print(i, db)
    if return_ls:
        return db_menu(PATH_TO_CONFIG, CONFIG_FILE).ls_db # return list of db in config file
    #p.prompt_menu(msg="Enter an integer to intialize db", ls=ls_output)
    # TO-DO: this^ only returns the str of the database name at hte moment

def config():
    """opens the db_config.ini file"""
    os.startfile(PATH_TO_CONFIG / CONFIG_FILE)

c = config_class()
PATH_TO_CONFIG, CONFIG_FILE = c.init_config_path