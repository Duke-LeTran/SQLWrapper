"""
sqlwrapper.py
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
#setup
#from sqlwrapper.sqlwrapper import *
#from sqlwrapper.config import PATH_TO_CONFIG, CONFIG_FILE
from sqlwrapper.config import config_reader
from sqlwrapper.dbmenu import connect, db_menu
config = config_reader()
menu = db_menu()
#from sqlwrapper.config import _resolve_path_to_config, ls_path_to_config, ls_config_file
#PATH_TO_CONFIG, CONFIG_FILE = _resolve_path_to_config(ls_path_to_config, ls_config_file)


from sqlwrapper.prompter import Prompter
from sqlwrapper.df_tools import max_len_cols
from sqlwrapper.xlsx import read_xlsx, sheet_to_df

# database connections
from sqlwrapper.base import SQL
from sqlwrapper.oracle import Oracle
from sqlwrapper.mariadb import MariaDB
from sqlwrapper.sqlserver import SQLServer


