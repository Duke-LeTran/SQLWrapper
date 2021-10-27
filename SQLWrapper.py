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

# standard library
import urllib
from getpass import getpass
from pathlib import Path
from configparser import ConfigParser

# personal libs
from prompter import Prompter

# db drviers 
import pandas as pd
import pyodbc #SQL Server 
import cx_Oracle #oracle
import sqlalchemy as sqla

# setup
p = Prompter()
PATH_TO_CONFIG = Path.home() / Path('.mypylib')
CONFIG_FILE = 'db_config.ini' #name of your config file

def ls(return_ls=False):
    """prints list of db in config file"""
    print("DATABASES\n-----")
    for i, db in enumerate(db_menu().ls_db):
        print(i, db)
    if return_ls:
        return db_menu().ls_db # return list of db in config file
    #p.prompt_menu(msg="Enter an integer to intialize db", ls=ls_output)
    # TO-DO: this^ only returns the str of the database name at hte moment

class db_menu:
    """
    Manages the config file
    SET-UP:
        * path_to_config
        * db_config.ini file
    """
    def __init__(self, opt_print=True):
        """Windows Config Utils, create child class as necessary"""
        self.__setup_options() #get setup options
        self.__ls_db(opt_print=opt_print) # get list of db from config files
        self.db_selected = None
        
    def __setup_options(self):
        """
        SETUP: These need to be setup once before use
        """
        self.path_to_config = PATH_TO_CONFIG
        self.db_config = CONFIG_FILE
    
    def __ls_db(self, opt_print):
        """# get list of db from config files"""
        config = self.__init_config(opt_print=opt_print)
        self.ls_db = config.sections()
    
    def __init_config(self, db=None, opt_print=True):
        config = ConfigParser() #keep local
        path = self.path_to_config / self.db_config #self.d_db[self.db_type]
        if opt_print and db is not None:
            print(f'Initializing database using config file from {path} using [{db}].')
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
        config = self.__init_config(db)
        if db is None: # if none, prompt for database
            db_menu = self.prompt_db()
        else:
            db_menu = db # else, use the database provided
        return config[db_menu]
    
class SQL: # level 0
    """ABSTRACT BASE CLASS"""
    def __init__(self, db_name='Duke', schema_name='dbo'):
        self.db_name = db_name
        self.schema_name= schema_name
        self.prefix = db_name + '.' + schema_name
        # self.msg_inaction = "No action taken. Remember to rollback or commit."
        self.sqlHx = pd.Series()
        self.p = Prompter()

    def _generate_cursor(self):
        self.cursor = self.conn.cursor()
    
    def _save_config(self, config):
        """obfuscates pw; saves config obj"""
        config['world'] = 'hello'
        self.config = config
        
    def read_sql(self, sql_statement):
        """ Imitation of the pandas read_sql"""
        sql = self.readify_sql(sql_statement)
        print(sql)
        return pd.read_sql(sql, self.engine)
    
    @staticmethod
    def readify_sql(sql_input):
        return (' ').join(sql_input.replace('\n','').split())
        
    def save_sql_hx(self, sql_statement):
        sql_statement = ' '.join(sql_statement.split()) #remove extra whitespace
        print(sql_statement)
        self.sqlHx = self.sqlHx.append(pd.Series(sql_statement), ignore_index=True)

    def close(self):
        self.__del__()
    
    @staticmethod
    def select_cols(cols):
        if type(cols) is list: # if list is provided
            if len (cols) > 0:
                col_names = ", ".join(cols)
            else: 
                col_names = cols[0] # grab str of first and only item
            return col_names
        elif type(cols) is str: # if only one column provided as str
            return cols
    
    @staticmethod
    def check_schema(schema, schema_default):
        if schema is not None: #if schema is defined
            prefix = f'{schema}'
        else: # else use default
            prefix = f'{schema_default}'
        return prefix
    
    @staticmethod
    def where(sql_statement, where):
        if where:
            sql_statement = f"{sql_statement} WHERE {where}"
        return sql_statement  
    
    @staticmethod
    def order_by(sql_statement:str, orderby:str, desc:bool):
        sql_statement = f"{sql_statement} ORDER BY {orderby}"
        if desc:
            sql_statement = f"{sql_statement} DESC"
        return sql_statement
                
        
    def __del__(self):
        try:
            self.engine.dispose()
            self.cursor.close()
            self.conn.close()
        except AttributeError:
            pass

class SQLServer(SQL): # level 1
    """
    SQL Server Database Wrapper
    Set-up: authentication config
    """
    def __init__(self, db_config='OMOP_DeID', schema_name='dbo', trusted='yes', opt_print=True):
        # attempt ot initizlie
        db_menu = db_menu(opt_print=opt_print)
        if db_config is None:
            db_config = db_menu.prompt_db()
        try:
            config = db_menu.read_config(db_config) #keep local
        except KeyError:
            print('\nERROR: Attempted to init an Oracle db.Try again.')
            return
        super(SQLServer, self).__init__(config['DATABASE'], schema_name)
        self.trusted_bool = trusted
        self._connect(config)
        self._generate_dbinfo()
        self._save_config(config)

    def __del__(self):
        msg_closed_success = 'Both the cursor and connection are successfully closed.'
        try:
            super().__del__()
            print(f'{msg_closed_success}')
        except pyodbc.ProgrammingError:
            try:
                self.conn.close()
                print(f'Cursor previously closed. {msg_closed_success}')
            except pyodbc.ProgrammingError:
                print(f'{msg_closed_success}')
                
    def _generate_conn_string(self, config, pw=None):
        if config['UID'] is None:
            self.conn_string = (f"DRIVER={config['DRIVER']};" \
                                f"SERVER={config['SERVER']};" \
                                f"DATABASE={config['DATABASE']};" \
                                f"TRUSTED_CONNECTION={self.trusted_bool};")
                               #f"UID=user;" \ # MUST delete trusted connection
                               #f"PWD=password"
        else:
            self.conn_string = (f"DRIVER={config['DRIVER']};" \
                               f"SERVER={config['SERVER']};" \
                               f"DATABASE={config['DATABASE']};" \
                               f"UID={config['UID']};" \
                               f"PWD={pw}")
                               #f"TRUSTED_CONNECTION={self.trusted_bool};")
        self.url_conn_string = urllib.parse.quote_plus(self.conn_string)
        
    def _generate_connection(self, config, pw=None):
        self.conn = pyodbc.connect(self.conn_string, uid=config['UID'], pw=pw)

    
    def _generate_engine(self):
        self.omop_string = (f'mssql+pyodbc:///?odbc_connect=' \
                                         f'{self.url_conn_string}')
        self.engine = sqla.create_engine(self.omop_string)

    def _connect(self, config, pw=None):
        if config['UID'] is not None:
            pw = getpass()
        self._generate_conn_string(config, pw=pw)
        self._generate_connection(config, pw=pw)
        self._generate_engine()
        self._generate_cursor()
        print('New connection successfully established.')
    

    def _generate_dbinfo(self):
            sql_long = (f"SELECT TABLE_CATALOG as db_name," \
                        f"       TABLE_SCHEMA as schema_name," \
                        f"       TABLE_NAME as tbl_name," \
                        f"       COLUMN_NAME as col_name," \
                        f"       DATA_TYPE," \
                        f"       CHARACTER_MAXIMUM_LENGTH," \
                        f"       NUMERIC_PRECISION " \
                        f"FROM " \
                        f"    INFORMATION_SCHEMA.COLUMNS;")
            sql_short = (f"SELECT TABLE_CATALOG as db_name," \
                         f"       TABLE_SCHEMA as schema_name," \
                         f"       TABLE_NAME as tbl_name," \
                         f"       COLUMN_NAME as col_name " \
                         f"FROM " \
                         f"    INFORMATION_SCHEMA.COLUMNS;")
            self.df_info = pd.read_sql(sql_short, self.conn)
            self.df_info_Long = pd.read_sql(sql_long, self.conn)

    def update_conn(self):
        """
        Updates the connection. Things to change:
            self.config['SERVER']
            self.config['DATABASE']
            self.config['world']
            self.schema_name
        """
        self.conn.close()
        #reconnect
        self._connect(self.config)
        self._generate_dbinfo()
        self._save_config(self.config)
        
    def update_df(self, df_input, tbl_name):
        """update dataframe to database"""
        if tbl_name in set(self.info()['tbl_name']): #if df is a tbl in db
            if p.prompt_confirmation('Table already exists. Confirm overwrite?'):
                x = 'replace'
        df_input.to_sql(tbl_name, self.engine, if_exists=x)
        self._generate_dbinfo #update info
        
    def ls_schema(self):
        sql_statement = (f"SELECT s.schema_id," \
                         f"    s.name as schema_name," \
                         f"    u.name as schema_owner " \
                         f"FROM " \
                         f"    SYS.SCHEMAS s " \
                         f"INNER JOIN" \
                         f"    SYS.SYSUSERS u " \
                         f"ON u.uid = s.principal_id " \
                         f"ORDER BY s.name;")
        return pd.read_sql(sql_statement, self.conn)
    
    def ls_tbl(self, user_input=None):
        s = pd.Series(self.info()[['schema_name','tbl_name']].values.tolist())
        s = s.apply('.'.join)
        s = s.drop_duplicates().reset_index(drop=True)
        ls =  self.info()['tbl_name'].drop_duplicates().tolist()
        if user_input is None:
            try:
                user_input = int(input('Return (1) ls (2) pd.s (3) or both? >> '))
            except ValueError: #return s if user_input error
                return s
        #if user_input is sucessful
        if user_input == 1:
            return ls
        elif user_input == 3:
            return s, ls
        else:
            return s

    def info(self, long_bool=False):
        if long_bool:
            return self.df_info_Long
        else:
            return self.df_info
        
    def info2(self, schema_name='dbo'):
        df = self.df_info[self.df_info['schema_name'] == schema_name]
        df.reset_index(drop=True,inplace=True)
        
        df_output = df.groupby('tbl_name').count()['col_name'].reset_index()
        df_output.columns = ['tbl_name', 'col_count']
        
        ls_rowcount = []
        # parse for number of rows
        for tbl_name in df_output['tbl_name']:
            sql_statement = f"SELECT COUNT(*) FROM {tbl_name}"
            int_row = pd.read_sql(sql_statement, self.conn).iloc[0,0]
            #print(tbl_name, ', row_count:', int_row)
            ls_rowcount.append(int_row)
            
        df_output['row_count'] = ls_rowcount # add row count column  
        df_output['shape'] = list(zip(df_output.col_count, df_output.row_count)) # add tuple, ie, shape of tables
        return df_output
        
    def scope(self):
        print('Current Scope...\n',
              'Server:', self.config['SERVER'], '\n',
              'Database:', self.config['DATABASE'], '\n', 
              'Schema:', self.schema_name, '\n')

    @staticmethod
    def limit(col_names, limit, prefix, tbl_name):
        if type(limit) is int: # LIMIT # if SELECT TOP is defined correctly as int
            sql_statement = f"SELECT TOP ({limit}) {col_names} FROM {prefix}.{tbl_name}"
        else: # else select all
            sql_statement = f"SELECT {col_names} FROM {prefix}.{tbl_name};"
        return sql_statement
    
    def count(tbl_name):
        return pd.read_sql("SELECT COUNT(*) FROM {tbl_name}.")
    
    def select(self, cols, tbl_name, limit=None, schema=None, where=None, order_by=None, print_bool=True, desc=0):
        """returns a pd.DataFrame"""
        # SELECT COLS
        col_names = self.select_cols(cols) 
        # SCHEMA
        prefix = self.check_schema(schema, self.schema_name)
        # LIMIT - select TOP goes in front in SQLServer, hence the 
        sql_statement = self.limit(col_names, limit, prefix, tbl_name)
        # WHERE
        sql_statement = self.where(sql_statement, where)
        # ORDER BY
        sql_statement = self.order_by(sql_statement, cols, order_by, desc)
        # LOG
        if print_bool:
            self.save_sql_hx(sql_statement)
            return pd.read_sql(sql_statement, self.conn)

    def sql(self, sql_statement):
        """For typing out whole generic SQL statements; no checks"""
        pd.read_sql(sql_statement, self.conn)
        
    def insert(self, tbl_name, data_values, schema=None):
        pass
    
    def insert_csv(self, tbl_name, csv_path):
        """inserts dataframe"""
        df_input = pd.read_csv(csv_path)
        self.insert_df(tbl_name, df_input)
    
    def insert_df(self, tbl_name, df_input, schema=None, method='multi'):
        if schema is None:
            schema=self.schema_name
        df_input.to_sql(tbl_name,
                        con=self.engine,
                        method=method,
                        schema=schema)
        self._generate_dbinfo() #update info
        

class Oracle(SQL): # level 1
    """
    Oracle Database Wrapper
    Things to note in Oracle:
        * schemas == users
        * hostname == server
        * service_name == nickname of tnsaora file
    """
    def __init__(self, config='Velos', opt_print=False): #defaults to Velos
        config = db_menu(opt_print=opt_print).read_config(db=config) # local variable not saved
        super(Oracle, self).__init__(schema_name=config['hello']) # username is schema
        self._connect(config)
        self._save_config(config)

    def __del__(self):
        self.engine.dispose()
        self.conn.close()

    def _connect(self, config):
        self._generate_engine(config)
        self._generate_connection(config)
        #self._generate_cursor()

    def _generate_engine(self, config):
        """ 
        This assumse you have all your Oracle ENV variables set correctly, e.g.
        * ORACLE_BASE=/opt/oracle
        * ORACLE_HOME=$ORACLE_BASE/full_or_instant_client_home
        * TNS_ADMIN=$ORACLE_HOME/network/admin
        * (full) LD_LIBRARY_PATH=$ORACLE_HOME/lib:$LD_LIBRARY_PATH
        * (instant) LD_LIBRARY_PATH=$ORACLE_HOME:$LD_LIBRARY_PATH

        """
        # dsn = cx_Oracle.makedsn(config['hostname'], config['port'], service_name=config['service_name'])
        self.engine = sqla.create_engine(\
            f"oracle+cx_oracle://{config['hello']}:{config['world']}@{config['db_alias']}",
            connect_args={"encoding":"UTF-8"},
            max_identifier_length=128) # this removes warnings

    def _generate_connection(self, config):
            #conn_string = f"{config['hello']}/{config['world']}@{config['hostname']}/{config['service_name']}"
            #self.conn = cx_Oracle.connect(conn_string)
            self.conn = self.engine.connect() # sqla connection

    def ls_schema(self):
        sql_statement = (f'SELECT username AS schema_name ' \
                         f'FROM ' \
                         f'    SYS.all_users ' \
                         f'ORDER BY ' \
                         f'    username')
        print(self.readify_sql(sql_statement))
        return pd.read_sql(self.readify_sql(sql_statement), self.engine)

    def print_scope(self):
        print('Current Scope...\n',
              'Server:', self.config['hostname'], "#aka hostname", '\n',
              'Database:', self.config['db_name'], '\n', 
              'Schema/User:', self.schema_name, '\n')
    
    def version(self):
        str_version = self.conn.version
        ls_verStr = [int(x) for x in str_version.split('.')]
        d_ver = {10 : '10g',
                 11 : '11g',
                 12 : '12c',
                 1 : 'Release 1',
                 2 : 'Release 2'}
        print('Oracle Database', d_ver[ls_verStr[0]], d_ver[ls_verStr[1]], str_version)
        
    @staticmethod
    def limit(sql_statement, limit):
        if type(limit) is int: # if SELECT TOP is defined correctly as int
            sql_statement = (f"SELECT * FROM ({sql_statement}) " \
                             f"WHERE ROWNUM <= {limit}")
        return sql_statement
        
    def select(self,
               cols:list,
               tbl_name:str,
               schema:str=None,
               print_bool:bool=True,
               limit:str=None,
               where:str=None,
               order_by:str=None,
               desc:bool=False):
        """
        Function: returns a pd.DataFrame
        cols: list of columns
        tbl: table name
        schema: schema name (or default is selected)
        limit: limit number of rows
        """
        #SELECT
        col_names = self.select_cols(cols) 
        # SCHEMA
        prefix = self.check_schema(schema, self.schema_name)
        # SQL SKELETON
        sql_statement = f"SELECT {col_names} FROM {prefix}.{tbl_name}"
        # WHERE
        sql_statement = self.where(sql_statement, where)
        # ORDER BY
        sql_statement = self.order_by(sql_statement, cols, order_by, desc)
        # LIMIT
        sql_statement = self.limit(sql_statement, limit)
        # LOG
        if print_bool:
            self.save_sql_hx(sql_statement + ';')
        return pd.read_sql(sql_statement, con=self.conn)
    
    def insert(self):
        pass


