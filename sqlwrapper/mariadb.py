import logging
import sqlalchemy
from typing import Union
import pandas as pd


# from sqlwrapper import Prompter
from sqlwrapper.prompter import Prompter
from sqlwrapper.base import SQL
# from sqlwrapper.config import PATH_TO_CONFIG, CONFIG_FILE
from sqlwrapper.config import config_reader
from sqlwrapper.parameters import parameters, Missing_DBCONFIG_ValueError
from configparser import SectionProxy


log = logging.getLogger(__name__)

p = Prompter()


class MariaDB(SQL, parameters): # level 1
    """
    MariaDB Database Wrapper
    Things to note in Oracle:
        * schemas == users
        * hostname == server
        * service_name == nickname of tnsaora file`
    This assumse you have all your Oracle ENV variables set correctly, e.g.

    """
    def __init__(self, db_entry='redcap', opt_print=True, db_section:SectionProxy=None): 
        config = self._read_config(db_entry, opt_print)
        # initialize config
        self._init_config(db_section, db_entry, opt_print)
        self._save_config(config)
        super(MariaDB, self).__init__(schema_name=self._username) # username is schema
        self._connect()
    
    def _read_config(self, db_entry:str, opt_print:bool):
        config = config_reader().read(db_entry, opt_print)
        return config

    def _generate_conn_string(self) -> str:
        """generate connection string from config"""
        return f"{self._username}:{self._pw}@{self._hostname}:{self._port}/{self._database}"
    
    def _generate_engine(self):
        """ generate engine"""
         # A. generate using string method
        try:
            self.engine = sqlalchemy.create_engine(f"mariadb+pymysql://" \
                + self._generate_conn_string())
        except Exception as error:
            log.error(error)
        finally:
            self._test_connection(self._database)
    
    def _generate_inspector(self):
        from sqlalchemy import inspect
        self.inspector = inspect(self.engine)

    def _limit(self, sql_statement, limit):
        if limit == None:
            return sql_statement
        else:
            sql_statement += f' LIMIT {str(limit)}'
            return sql_statement

    def tables(self, silent=False):
        try:
            return list(self.read_sql('SHOW TABLES;', silent=silent)[f'Tables_in_{self._database}'])
        except Exception as error:
            log.error(error)

    def scope(self):
        print('[Current Scope]\n',
              'Hostname:', self._hostname.split('.')[0], '\n',
              'Database:', self._database.split('.')[0], '\n', 
              'User:', self.schema_name, '\n',
              'DB type:', self._config['db_type'])


    def columns(self,
                tbl_name:str,
                verbose=False,
                return_dtype=False) -> Union[pd.core.indexes.base.Index, list]:
        if verbose:
            return self.inspector.get_columns(tbl_name.lower())
        elif return_dtype:
            print('sqlalchemy docs: https://docs.sqlalchemy.org/en/14/dialects/mysql.html#mysql-data-types')
            df_dtype = pd.DataFrame(self.inspector.get_columns(tbl_name.lower(), dialect_options='mariadb'))
            return {k.upper():v for k,v in zip(df_dtype['name'], df_dtype['type'])}
        else:
            df_result = self.select(tbl_name, limit=1, print_bool=False)
            return df_result.columns

    def select(self,
               tbl_name:str,
               cols:Union[list, str]='*',
               schema:str=None,
               print_bool:bool=True,
               limit:int=10, # default to 10
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
        col_names = self._select_cols(cols) 
        # SCHEMA
        ## !TO-DO?
        # SQL SKELETON
        sql_statement = f"SELECT {col_names} FROM {tbl_name.lower()}"
        # WHERE
        sql_statement = self._where(sql_statement, where)
        # ORDER BYselect_cols
        sql_statement = self._order_by(sql_statement, cols, order_by, desc)
        # LIMIT
        if limit == None:
            pass
        else:
            sql_statement = self._limit(sql_statement, limit)
        # LOG
        if print_bool:
            self._save_sql_hx(sql_statement + ';')
        #df_output = pd.read_sql(sql_statement, self.engine)
        df_output = self.read_sql(sql_statement)
        # convert names to capital for consistency
        df_output.columns = [x.upper() for x in df_output.columns]
        return df_output

    def truncate(self, table:str, schema:str=None, engine=None, answer=None, tbl_lower=True):
        """
        You can use this to truncate other tables too, static method
        """
        # set defaults
        if schema is None:
            schema = self._database
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
        log.info(f"TRUNCATE TABLE {table}... ")
        log.info("=======================================================")
        cursor.execute(f"TRUNCATE TABLE {table}")
        log.info("Table truncated, done!")
        conn.close()

    def drop(self, tbl_name:str, what:str='TABLE', skip_prompt=False, answer=None):
        """For now this only drops tables, will expand in future to include sequences, etc."""
        if skip_prompt:
            answer = 'yes'
        #if tbl_name not in self.tables():
        #    print(f'Table {tbl_name} does not exist in the db. Nothing to drop.')
        #else:
        sql_statement = f'DROP {what} {tbl_name}'
        if p.prompt_confirmation(msg=f'Are you sure your want to drop {tbl_name}?', answer=answer):
            self.read_sql(sql_statement)

    def _process_df_insert_values(self, value):
        """
        * mariadb/mysql specific processing of VALUES
        """
        if pd.isnull(value): # set nulls to None
            return None
        else:
            return str(value) # set everything else to strings

    def insert(self, df_input, table, engine=None, cap_cols=False):
        # SET DEFAULTS #########################################################
        if cap_cols:
            df_input.columns = [x.upper() for x in df_input.columns]

        if engine is None:
            engine = self.engine

        # A. GENERATE CONN AND CURSOR ##########################################
        # conn = self.engine.raw_connection()
        # cur = conn.cursor()
    
        # B. GRAB COLS AS STRING ###############################################
        ## grab cols specifically from the database
        ls_cols = [x.lower() for x in self.columns(table).tolist()]
        ## convert cols to strings
        cols = (', '.join([x.lower() for x in ls_cols]))

        # C. CONVERT EACH VAL OF EACH ROW > STRING or None######################
        # VALUES
        func = lambda ls : [self._process_df_insert_values(x) for x in ls]
        # converts df to a list of string values 
        lines = [tuple(func(x)) for x in df_input[ls_cols].values]

        # D. BIND VARS
        ## mariadb/mysql uses '%s'
        bind_vars = ', '.join(['%s' for x in range(len(df_input[ls_cols].columns))])
        # bind_vars = ''
        # for i in range(len(df_input[cols].columns)):
        #     bind_vars = bind_vars + '%s, '
        # ## remove trailing
        # bind_vars = bind_vars[:-2]

        # E. GENERATE INSERT STATEMENT #########################################
        ## validate length, debug only
        # assert len(ls_cols) == max(map(len, lines)), f"Number of VALUES {len(ls_cols)} exceeds COLS {max(map(len, lines))}"
        # assert len(ls_cols) ==len(bind_vars.split(', ')) , f"Number of BIND_VARS {len(ls_cols)} exceeds COLS {len(bind_vars.split(', '))}"

        ## generate sql statement
        sql = f'INSERT INTO {table.lower()} ({cols}) values ({bind_vars})'


        # F. EXECUTE SQL #######################################################
        log.info('=======================================================')
        log.info(f' pymysql EXECUTEMANY, INSERT INTO {table}')
        log.info('=======================================================')
        try:
            conn = self.engine.raw_connection()
            with conn.cursor() as cur: # a good practice to follow
                cur.executemany(sql, lines)

            conn.commit()
        except Exception as e:
            log.warning(e)
        finally:
            conn.close





