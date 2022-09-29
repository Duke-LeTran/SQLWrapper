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
from pathlib import Path

# SQLWrapper
from sqlwrapper.dbmenu import db_menu
from sqlwrapper.prompter import Prompter

# logging
log = logging.getLogger(__name__)

# setup
PATH_TO_CONFIG = Path.home() / Path('.mypylib')
CONFIG_FILE = 'db_config.ini' #name of your config file

# prompter
p = Prompter()

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
    