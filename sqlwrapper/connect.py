from typing import Union
from pathlib import Path, PurePath
from sqlwrapper.dbmenu import db_menu
from dotenv import load_dotenv
from pathlib import Path
import hvac
import logging
#import df_tools
import os
import traceback

log = logging.getLogger(__name__)
################################################################################
# db = sqlwrapper.connect
################################################################################
def connect_vault(sec_path='rifr/ProfilesProd',
                  db_entry:str=None,
                  env_path=Path.cwd() / '.env'):
    """ 
    Vault Support
    * default path for env path is current directory
    """
    load_dotenv(env_path)
    #load_dotenv(Path.home() / '.mypylib' / '.env')
    vault_client = hvac.Client(url=os.environ.get('VAULT_SERVER'),
                               token=os.environ.get('VAULT_TOKEN'))
    map_secrets = vault_client.read(sec_path)['data']
    ## DEBUG ###
    print(' connecting via Vault '.center(80, '='))
    print(os.environ.get('VAULT_SERVER').center(80, ' ') )
    print('='*80)
    menu = db_menu()
    return menu.connect(sec_path=sec_path, map_secrets=map_secrets)
    # convert this to config reader entry
    # use entry to return database

def connect_db_config(db_entry):
    """connect via db_config.ini file"""
    menu = db_menu()
    db = menu.connect(db_entry)
    return db 

def connect(db_entry:str=None, sec_path:str=None, **kwargs):
    """
    Pass the db config entry to connect. Use ls() or entries() if you don't
    remember.
    """
    if sec_path is not None:
        return connect_vault(sec_path=sec_path, db_entry=db_entry)
    else:
        return connect_db_config(db_entry)
