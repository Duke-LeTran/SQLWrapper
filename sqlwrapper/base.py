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
# standard library
import logging
import os
# added libraries
import pandas as pd
from sqlalchemy import exc
# SQLWrapper
from SQLWrapper.config import PATH_TO_CONFIG, CONFIG_FILE
from SQLWrapper.prompter import Prompter

# logging
log = logging.getLogger(__name__)

p = Prompter()


class SQL: # level 0
    """ABSTRACT BASE CLASS"""
    def __init__(self, db_name='Duke', schema_name='dbo'):
        self.db_name = db_name
        self.schema_name= schema_name
        self.prefix = db_name + '.' + schema_name
        # self.msg_inaction = "No action taken. Remember to rollback or commit."
        self.sqlHx = pd.Series(dtype='object')
        self.p = Prompter()

    # def _generate_cursor(self):
    #     self.cursor = self.conn.cursor()
    
    
    def _save_config(self, config):
        """obfuscates pw; saves config obj"""
        #config['world'] = 'hello'
        self.config = config
    
    @staticmethod    
    def config():
        os.startfile(PATH_TO_CONFIG / CONFIG_FILE)
    
    def truncate(self, table:str, schema:str=None, engine=None, answer=None):
        """
        You can use this to truncate other tables too, static method
        """
        # set defaults
        if schema is None:
            schema = self.schema_name
        if engine is None:
            engine = self.engine
        
        # prompt for confirmation
        if not p.prompt_confirmation(answer=answer): # if user denies
            print('Did not truncate, canceled by user.')

        # create connection and truncate
        conn = engine.raw_connection()
        cursor = conn.cursor()
        log.info("=======================================================")
        log.info(f"TRUNCATE TABLE {schema}.{table}... ")
        log.info("=======================================================")
        cursor.execute(f"TRUNCATE TABLE {schema}.{table}")
        log.info("Table truncated, done!")
        conn.close()
    
    def drop(self, tbl_name:str, what:str='TABLE', skip_prompt=False, answer=None):
        """For now this only drops tables, will expand in future to include sequences, etc."""
        if skip_prompt:
            answer = 'yes'
        if tbl_name not in self.tables():
            print(f'Table {tbl_name} does not exist in the db. Nothing to drop.')
        else:
            sql_statement = f'DROP {what} {self.schema_name}.{tbl_name}'
            if p.prompt_confirmation(msg=f'Are you sure your want to drop {tbl_name}?', answer=answer):
                self.read_sql(sql_statement)
    
    @staticmethod
    def merge_frames(frames:list, on:str=None):
        """
        Parameters: pass a list of dataframes
        Notes:
        * Uses recursion to merge frames
        * similar to pd.concat()
        * will merge on single-to-many keys -- SO BECAREFUL 
        """
        if on is None:
            print('You must pass a key to merge on. Use parameter "on=your_key".')
            return
        print('❤️' * len(frames))
        if len(frames) > 2: # if more than 2 dataframes
            # pass deeper
            ##time.sleep(1)
            result = merge_frames(frames[:-1], on=on) # drop the last one
            # merge some action item
            print('🌱' * len(frames))
            ##time.sleep(1)
            result = pd.merge(result, frames[-1])
            return result
        else: # else only two left..
            ##time.sleep(1)
            print('BOTTOM!!')
            print('🌱' * len(frames))
            # merge first pair of dataframes
            return pd.merge(frames[0], frames[1], on=on)
    
    def read_sql(self, sql_statement, silent=False):
        """ Imitation of the pandas read_sql"""
        sql = self.readify_sql(sql_statement)
        if not silent:
            print(sql)
        try:
            return pd.read_sql(sql, self.engine)
        except exc.ResourceClosedError as error:
            pass # if no rows returned

    # @property
    # def schema(self):
    #     return self.schema_name
    
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
    def order_by(sql_statement:str, cols:list, order_by:str, desc:bool):
        if order_by:
            sql_statement = f"{sql_statement} ORDER BY {order_by}"
        if desc:
            sql_statement = f"{sql_statement} DESC"
        return sql_statement
                
    def tables(self):
        try:
            return sorted(self.inspector.get_table_names())
        except Exception as error:
            log.error(error)
    
    def __del__(self):
        from cx_Oracle import OperationalError
        try:
            self.engine.dispose()
            #self.cursor.close()
            #self.conn.close()
        except AttributeError as error:
            log.info(error)
        except InterfaceError as error:
            log.info(error)
        except OperationalError as error:
            log.info('db.engine likely idled and already closed, don\'t worry.')
            log.info(error)

