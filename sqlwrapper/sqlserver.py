import logging
import urllib
from sqlalchemy.engine import URL
from sqlalchemy import create_engine, inspect
import pyodbc
import pandas as pd
from typing import Union
from sqlwrapper.base import SQL
from sqlwrapper.prompter import Prompter
from sqlwrapper.config import config_reader
from sqlwrapper.parameters import parameters, Missing_DBCONFIG_ValueError
from configparser import SectionProxy

from getpass import getpass

# logging
log = logging.getLogger(__name__)

# prompter
p = Prompter()

class SQLServer(SQL, parameters): # level 1
    """
    SQL Server Database Wrapper
    Set-up: authentication config
    """
    def __init__(self,
                 db_entry='OMOP_DeID',
                 schema_name='dbo',
                 trusted='yes',
                 opt_print=True,
                 db_section:SectionProxy=None):
        # initialize config
        config = self._init_config(db_section, db_entry, opt_print)
        self._save_config(config)
        super(SQLServer, self).__init__(db_name=self._database, 
                                        schema_name=schema_name)
        self.trusted_bool = trusted
        self.engine=None
        self._connect()
        self._generate_dbinfo()
        #self._save_config(config)
                
    def _generate_conn_string(self):
        """
        generates conn_string, also selects driver
        """
        # if FreeTDS driver
        if self._driver.lower() in "{freetds}":
            return self._generate_freetds_conn_string()
        else: # if official microsoft ODBC drivers
            return self._generate_mssql_conn_string()


    def _generate_mssql_conn_string(self):
        """ 
        Driver: {ODBC Driver 17 for SQL Server}: 
        * Generates conn_string using encoded odbc_connect method
        * supports windows auth
        """
        try: # sql auth
            conn_string = (f"DRIVER={self._driver};" \
                               f"SERVER={self._hostname};" \
                               f"DATABASE={self._database};" \
                               f"UID={self._username};" \
                               f"PWD={self._pw}")
        except Missing_DBCONFIG_ValueError as e: #windows auth
            log.warning("Attemping to connect with Windows Auth...")
            conn_string = (f"DRIVER={self._driver};" \
                           f"SERVER={self._hostname};" \
                           f"DATABASE={self._database};" \
                           f"TRUSTED_CONNECTION={self.trusted_bool};")
        encoded_url_string = urllib.parse.quote_plus(conn_string)
        return f'mssql+pyodbc:///?odbc_connect={encoded_url_string}'

    def _generate_freetds_conn_string(self):
        """
        Driver: FreeTDS
        """
        from sqlalchemy.engine import URL
        from getpass import getpass

        # conn_string = URL.create(
        #     "mssql+pyodbc",
        #     username=config['hello'],
        #     password=getpass(),
        #     host=config['SERVER'],
        #     port=config['PORT'],
        #     database=config['DATABASE'],
        #     query={
        #         "driver": "FreeTDS", # this hard-coded for standarization
        #     },
        # )
        conn_string = URL.create(
            "mssql+pyodbc",
            username=self._hello,
            password=getpass(),
            host=self._hostname,
            port=self._port,
            database=self._database,
            query={
                "driver": "FreeTDS", # this hard-coded
            },
        )
        return conn_string

    def _generate_engine(self):
        """
        https://docs.sqlalchemy.org/en/20/dialects/mssql.html
        https://stackoverflow.com/a/48861231/9335288
        """
        conn_string = self._generate_conn_string()
        try:
            self.engine = create_engine(conn_string, fast_executemany=True)
        except Exception as e:
            log.warning(e)
            self.engine = create_engine(conn_string)
        except Exception as e:
            log.error(e)
            raise
        finally:
            self._test_connection(self.prefix)

    def _generate_inspector(self):
        self.inspector = inspect(self.engine)

    def _flush(self):
        self.inspector=None
        self.engine=None
    
    def _reconnect(self):
        self.engine.dispose()
        #self.engine = None
        # config = self._config
        # conn_string = (f"DRIVER={config['DRIVER']};" \
        #                        f"SERVER={config['SERVER']};" \
        #                        f"DATABASE={config['DATABASE']};" \
        #                        f"UID={config['hello']};" \
        #                        f"PWD={config['world']}")
        # self.encoded_url_string = urllib.parse.quote_plus(conn_string)
        self._flush()
        self._generate_engine()
        self._generate_inspector()

    def use(self, db_name=None, schema_name=None):
        """USE DATABASE <new-db-name>;"""
        if db_name is None:
            print(f'Already current db; no changes to db_name {self.db_name}')
            return

        if schema_name is None:
            schema_name = self.schema_name

        print(f'Current database: {self.prefix}')
        print(f'Change to database: {db_name}.{self.schema_name}')
        msg='Are you sure you want to change databases?'
        if self.p.prompt_confirmation(msg=msg):
            self._config['DATABASE'] = db_name
            self.db_name = db_name
            self.prefix = db_name + '.' + schema_name
            self._reconnect()

    def use_db(self, db_name=None):
        """USE DATABASE <new-db-name>;"""
        if db_name is None:
            print(f'No changes to db_name {self.db_name}')
            return
        print(f'Current database: {self.prefix}')
        print(f'Change to database: {db_name}.{self.schema_name}')
        msg='Are you sure you want to change databases?'
        if self.p.prompt_confirmation(msg=msg):
            self.db_name = db_name
            self.prefix = db_name + '.' + self.schema_name

    def change_schema(self, schema_name=None):
        """ALTER SCHEMA <new-schema-name>;"""
        if schema_name is None:
            print(f'Already current db; no changes to schema_name {self.schema_name}')
            return
        print(f'Current database: {self.prefix}')
        print(f'Change to database: {self.db_name}.{schema_name}')
        msg='Are you sure you want to change databases?'
        if self.p.prompt_confirmation(msg=msg):
            #self._config['DATABASE'] = schema_name
            self.schema_name = schema_name
            self.prefix = self.db_name + '.' + schema_name
            #self._reconnect() # you don't need to reconnect
    

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
            self.df_info = pd.read_sql(sql_short, self.engine)
            self.df_info_Long = pd.read_sql(sql_long, self.engine)

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
            int_row = pd.read_sql(sql_statement, self.engine).iloc[0,0]
            #print(tbl_name, ', row_count:', int_row)
            ls_rowcount.append(int_row)
            
        df_output['row_count'] = ls_rowcount # add row count column  
        df_output['shape'] = list(zip(df_output.col_count, df_output.row_count)) # add tuple, ie, shape of tables
        return df_output
        
    def scope(self):
        print('[Current Scope]\n',
              'Server:', self._config['SERVER'], '\n',
              'Database:', self._config['DATABASE'], '\n', 
              'Schema:', self.schema_name, '\n')

    @staticmethod
    def _limit(col_names, limit, prefix, tbl_name):
        if type(limit) is int: # LIMIT # if SELECT TOP is defined correctly as int
            sql_statement = f"SELECT TOP ({limit}) {col_names} FROM {prefix}.{tbl_name}"
        else: # else select all
            sql_statement = f"SELECT {col_names} FROM {prefix}.{tbl_name}"
        return sql_statement
    
    @staticmethod
    def _get_database(prefix, database, database_default):
        """ check if schema is defined, else use default"""
        if database is not None: #if database is defined
            database = f'{database}'
        else: # else use default
            database = f'{database_default}'
        prefix = f'{database}.{prefix}'
        return prefix

    def count(tbl_name):
        return pd.read_sql("SELECT COUNT(*) FROM {tbl_name}.")
    
    def select(self, 
               tbl_name:str,
               cols:Union[list, str]='*',
               #cols, tbl_name,
               database:str=None,
               schema:str=None,
               print_bool:bool=True,
               limit:int=10, # default to 10
               where:str=None,
               order_by:str=None,
               desc:bool=False):
        """returns a pd.DataFrame"""
        # SELECT COLS
        col_names = self._select_cols(cols) 
        # SCHEMA
        prefix = self._get_schema(schema, self.schema_name)
        # DATABASE
        prefix = self._get_database(prefix, database, self.db_name)
        # LIMIT - select TOP goes in front in SQLServer, hence the 
        sql_statement = self._limit(col_names, limit, prefix, tbl_name)
        # WHERE
        sql_statement = self._where(sql_statement, where)
        # ORDER BY
        sql_statement = self._order_by(sql_statement, cols, order_by, desc)
        # LOG
        if print_bool:
            self._save_sql_hx(sql_statement + ';')
        df_output = pd.read_sql(sql_statement, self.engine)
        # convert names to capital for consistency
        #df_output.columns = [x.upper() for x in df_output.columns]
        return df_output

    def columns(self,
                tbl_name:str,
                verbose=False,
                return_dtype=False) -> Union[pd.core.indexes.base.Index, list]:
        """https://docs.sqlalchemy.org/en/14/dialects/mssql.html#sql-server-data-types"""
        if verbose:
            return self.inspector.get_columns(tbl_name.lower())
        elif return_dtype:
            print('https://docs.sqlalchemy.org/en/14/dialects/mssql.html#sql-server-data-types')
            df_dtype = pd.DataFrame(self.inspector.get_columns(tbl_name.lower(), dialect_options='mssql'))
            return {k.upper():v for k,v in zip(df_dtype['name'], df_dtype['type'])}
        else:
            df_result = self.select(tbl_name, limit=1, print_bool=False)
            return df_result.columns

    def tables(self, verbose=False):
        if verbose:
            ls_cols = [
                'schema_name(schema_id) schema_name', 
                'name tbl_name',
                'type', 
                'type_desc', 
                'create_date', 
                'modify_date'
            ]
            sql_statement = f"select {', '.join(ls_cols)} "
            sql_statement += "FROM sys.tables "
            sql_statement += "ORDER BY name"
            return self.read_sql(sql_statement)
        else:
            sql_statement = "select name FROM sys.tables ORDER BY name"
            return list(self.read_sql(sql_statement)['name'])



    def schemas(self, verbose=False) -> list:  
        """ returns a list of schemas, no verbose option """
        ls_exclude = [
            'db_accessadmin',
            'db_backupoperator',
            'db_datareader',
            'db_datawriter',
            'db_ddladmin',
            'db_denydatareader',
            'db_denydatawriter',
            'db_owner',
            'db_securityadmin',
            'sys',
            'INFORMATION_SCHEMA',
            'guest'
        ]
        ls_exclude = [f"'{x}'" for x in ls_exclude] # add quotes around strings
        sql_statement = "SELECT name FROM sys.schemas "
        sql_statement += f"WHERE name not in "
        sql_statement += f"({', '.join(ls_exclude)}) "
        sql_statement += "AND name not like 'HS\\%'"
        sql_statement += "ORDER BY name"
        return list(self.read_sql(sql_statement)['name'])


    def databases(self, verbose=False):
        """returns a list of all databases"""
        ls_exclude = ['master','tempdb','model','msdb']
        ls_exclude = [f"'{x}'" for x in ls_exclude]
        sql_statement = "SELECT name FROM sys.databases "
        sql_statement += "WHERE name not in "
        sql_statement += f"({', '.join(ls_exclude)}) " 
        return list(self.read_sql(sql_statement)['name'])

    def truncate(self, table:str,
                 database:str=None,
                 schema:str=None,
                 engine=None,
                 answer=None,
                 tbl_lower=True):
        """
        You can use this to truncate other tables too, static method
        """
        # set defaults
        if database is None:
            database = self.db_name
        if schema is None:
            schema = self.schema_name
        if engine is None:
            engine = self.engine
        
        # prompt for confirmation
        if not p.prompt_confirmation(answer=answer): # if user denies
            print('Did not truncate, canceled by user.')

        # table_name.lower()
        if tbl_lower == True:
            table = table.lower()

        # create connection and truncate
        conn = engine.raw_connection()
        cursor = conn.cursor()
        log.info("=======================================================")
        log.info(f"TRUNCATE TABLE {schema}.{table}... ")
        log.info("=======================================================")
        cursor.execute(f"TRUNCATE TABLE {schema}.{table}")
        log.info("Table truncated, done!")
        conn.close()

    def drop(self, tbl_name:str,
             what:str='TABLE',
             database:str=None,
             schema:str=None,
             skip_prompt=False,
             answer=None):
        """For now this only drops tables, will expand in future to include sequences, etc."""
        if skip_prompt:
            answer = 'yes'
        if tbl_name not in self.tables():
           print(f'Table {tbl_name} does not exist in the db. Nothing to drop.')
           return False
        if database is None:
            database = self.db_name
        if schema is None:
            schema = self.schema_name

        sql_statement = f'DROP {what} {database}.{schema}.{tbl_name}'
        if p.prompt_confirmation(msg=f'Are you sure your want to drop {tbl_name}?', answer=answer):
            self.read_sql(sql_statement)
    
    # def insert_csv(self, tbl_name, csv_path):
    #     """inserts dataframe"""
    #     df_input = pd.read_csv(csv_path)
    #     self.insert_df(tbl_name, df_input)
    
    # def insert_df(self, tbl_name, df_input, schema=None, method='multi'):
    #     if schema is None:
    #         schema=self.schema_name
    #     df_input.to_sql(tbl_name,
    #                     con=self.engine,
    #                     method=method,
    #                     schema=schema)

    def insert(self, df_input:pd.DataFrame,
                     table,
                     engine=None,
                     schema=None,
                     cap_cols=False,
                     index=False, # set default to False
                     if_exists='append', #sets default to append
                     method="multi", # sets default to multi
                     chunksize=1000,
                     **kwargs):
        """
        Since pd.DataFrame.to_sql() supports executemany() natively, this func
        only sets some defaults to my preferences. Otherwise, it effectively
        is the same.
        * https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_sql.html
        * https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#io-sql-method
        * execute_many:https://stackoverflow.com/a/48861231/9335288
        * https://docs.sqlalchemy.org/en/20/dialects/mssql.html#fast-executemany-mode
        """
        # SET DEFAULTS #########################################################
        if cap_cols:
            df_input.columns = [x.upper() for x in df_input.columns]

        if engine is None:
            engine = self.engine

        if schema is None:
            schema = self.schema_name

        # Convert to strings
        if method == 'multi':
            for col in df_input.columns:
                df_input.loc[:,col] = df[col].astype(str)

        # You can use pd.DataFrame.to_sql() for SQLServer!!
        df_input.to_sql(table,
            engine,
            if_exists=if_exists,
            index=index,
            schema=schema,
            method=method,
            chunksize=chunksize,
            **kwargs)