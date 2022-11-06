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
import pandas as pd

# SQLWrapper
#from sqlwrapper.dbmenu import db_menu
from sqlwrapper.prompter import Prompter
from typing import Union
from configparser import ConfigParser
# logging
log = logging.getLogger(__name__)

# setup
LS_PATH = [
    Path.home() / Path('.mypylib'),
    Path.cwd()
]

#name of your config file
LS_CONFIG_FILES = [
    'db_config.ini', 
    '.env',
    'config.env'
]

# prompter
p = Prompter()


class config_looker:
    """This looks for different config files on your computer"""
    def __init__(self, LS_PATH, LS_CONFIG_FILES):
        # setup
        self._init_paths(LS_PATH, LS_CONFIG_FILES)
    
    @property
    def current(self):
        return (self._PATH, self._FILE)
    
    @current.setter
    def current(self, values):
        try:
            self._PATH, self._FILE = values
            self._CONFIG = self._PATH / self._FILE
        except ValueError:
            raise ValueError("Pass an iterable with two items")
    
    @property
    def CONFIG(self):
        return self._CONFIG

    def _init_paths(self, PATH:list, FILE:list):
        self._LS_PATH = PATH
        self._LS_CONFIG_FILES = FILE
        for path in PATH:
            for file in FILE:
                if os.path.exists(path / file):
                    self.current = (path, file)
                    return path, file
    @property
    def config_path(self):
        return self._LS_PATH
    
    def append_path(self, path:Union[str, Path]):
        if type(path) == str:
            path = Path(path)
        self._LS_PATH.append(path)
        print(self.config_paths)

    @property
    def df_config(self):
        return self.df_config_all.loc[self.df_config_all['exists?'], :]

    @property
    def df_config_all(self):
        from os.path import exists
        return pd.DataFrame([(exists(path / file), path, file)
             for path in self._LS_PATH 
             for file in self._LS_CONFIG_FILES],
             columns=['exists?', 'path', 'file'])
    
    def select_config(self):
        ls_menu = [(x,y) for x,y in zip(self.df_config['path'], 
                                        self.df_config['file'])]
        new_config = p.prompt_menu('Select config', ls_menu)
        print(f"Old config: {self.current}")
        print(f"New config: {new_config}")
        self.current = new_config
    
    def open_config(self):
        """opens the db_config.ini file"""
        PATH_TO_CONFIG, CONFIG_FILE = self.current
        os.startfile(PATH_TO_CONFIG / CONFIG_FILE)


class config_reader(config_looker):
    def __init__(self):
        super(config_reader, self).__init__(LS_PATH, LS_CONFIG_FILES)
        self._init_config_path() #get setup options
    
    def _init_config_path(self):
        """
        SETUP: These need to be setup once before use
        """
        #self.config_looker = config_looker(LS_PATH, LS_CONFIG_FILES)
        path, file = self.current
        self._config_file = path / file
    
    @property
    def config_file(self):
        """this is the Path object to the config file"""
        return self._config_file
    
    @property
    def config(self):
        """the actual config file"""
        config = ConfigParser()
        config.read(self.CONFIG)
        return config
    
    @property
    def entries(self) -> list:
        config = self.config
        return sorted(list(config.keys()))
    
    def read(self, 
            db_entry:str=None,
            opt_print=True, 
            return_entry=True):
        msg = f'Initializing database connection from '
        msg += f'config file {self.CONFIG} using [{db_entry}].'
            
        if return_entry and db_entry is not None: # return only entry
            if opt_print:
                print(msg)
            return self.config[db_entry]
        else: # return entire config
            return self.config


# config_looker = config_looker(LS_PATH, LS_CONFIG_FILES)
# config_reader = config_reader()