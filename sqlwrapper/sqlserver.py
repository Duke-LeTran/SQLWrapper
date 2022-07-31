import logging
import urllib
import sqlalchemy
from getpass import getpass
import pyodbc
import pandas as pd

from SQLWrapper.base import SQL
from SQLWrapper.config import PATH_TO_CONFIG, CONFIG_FILE
from SQLWrapper.dbmenu import db_menu

# logging
log = logging.getLogger(__name__)

class SQLServer(SQL): # level 1
    """
    SQL Server Database Wrapper
    Set-up: authentication config
    """
    def __init__(self, config='OMOP_DeID', schema_name='dbo', trusted='yes', opt_print=True):
        # attempt ot initizlie
        config = db_menu(PATH_TO_CONFIG, CONFIG_FILE, opt_print=opt_print).read_config(db=config) # local variable not saved
        if config is None:
            config = db_menu.prompt_db()
        #try:
        #    config = db_menu.read_config(config) #keep local
        #except KeyError:
        #    print('\nERROR: Attempted to init an Oracle db.Try again.')
        #    return
        super(SQLServer, self).__init__(db_name=config['DATABASE'], 
                                        schema_name=schema_name)
        self.trusted_bool = trusted
        self.engine=None
        self._connect(config)
        self._generate_dbinfo()
        self._save_config(config)

    def __del__(self):
        msg_closed_success = 'Both the cursor and connection are successfully closed.'
        if self.engine:
            self.engine.dispose()
        # try:
        #     super().__del__()
        #     print(f'{msg_closed_success}')
        # except pyodbc.ProgrammingError:
        #     try:
        #         self.conn.close()
        #         print(f'Cursor previously closed. {msg_closed_success}')
        #     except pyodbc.ProgrammingError:
        #         print(f'{msg_closed_success}')
                
    def _generate_conn_string(self, config):
        if config['world'] is None: # if windows auth (no username)
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
                               f"UID={config['hello']};" \
                               f"PWD={config['world']}")
                               #f"TRUSTED_CONNECTION={self.trusted_bool};")
        self.encoded_url_string = urllib.parse.quote_plus(self.conn_string)
        return self.encoded_url_string
        
    # def _generate_connection(self, config):
    #     self.conn = pyodbc.connect(self.conn_string, 
    #         uid=config['hello'], 
    #         pw=config['world']
    #     )

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
    
    def _generate_engine(self):
        self.url_conn_string = (f'mssql+pyodbc:///?odbc_connect=' \
                                         f'{self.encoded_url_string}')
        self.engine = sqlalchemy.create_engine(self.url_conn_string)

    def _generate_inspector(self):
        from sqlalchemy import inspect
        self.inspector = inspect(self.engine)

    def _connect(self, config):
        if config['world'] is None:
            config['world']=getpass()
        else:
            pw=config['world']
        self._generate_conn_string(config)
        #self._generate_connection(config)
        self._generate_engine()
        self._generate_inspector()
        #self._generate_cursor()
        print(f'New connection successfully established to: {self.prefix}')
    

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
        print('[Current Scope]\n',
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
    
    def select(self, cols, tbl_name,
         limit=10, # limit to top 10, set to None if want all
         schema=None,
         where=None,
         order_by=None,
         print_bool=True,
         desc=False):
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
        
