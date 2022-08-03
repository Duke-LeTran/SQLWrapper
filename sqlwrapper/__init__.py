"""
SQLWrapper.py
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
#from SQLWrapper.SQLWrapper import *
from SQLWrapper.base import SQL
from SQLWrapper.config import PATH_TO_CONFIG, CONFIG_FILE
from SQLWrapper.dbmenu import db_menu
from SQLWrapper.prompter import Prompter
from SQLWrapper.df_tools import max_len_cols
from SQLWrapper.xlsx import read_xlsx, sheet_to_df

# database connections
from SQLWrapper.oracle import Oracle
from SQLWrapper.mariadb import MariaDB
from SQLWrapper.sqlserver import SQLServer



