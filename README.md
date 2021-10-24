# SQLWrapper

Assuming you have all your python environment setup correctly with the correct 
dependencies and/or modules, this tool should work very effectively with Oracle 
and SQLServer. 

# Setup
Set up you config files and ensure it is permissions protected.
```
cp -r config ~/.mypyblib
# edit your config files, i.e., db_config.ini
chmod 600 ~/.mypylib/* 
```

Add this `~/.bashrc` file.

```bash
export PYTHONPATH="~/path_to_module/SQLWrapper"
```

Now you should be able to import SQLWrapper from anywhere.
        
# Sample setup of config file: $HOME/.mypylib/db_config.ini
This is your config file. Entries will need to be edited to reflect your 
personal databases. See a few example entries below.

```{db_config.ini}
# I. Oracle
[OracleDb] 
hello = dletran
world = fakepw123
db_name = NameOfDatabase
hostname = HostName
service_name = ServiceName
port = 1521

# II. SQL SERVER
[SQLServerDb]
hello = dletran
DRIVER = {ODBC Driver 17 for SQL Server}
SERVER = NameOfServer
DATABASE = NameOfDatabase
```


# Sample Use

```{python}
import pandas as pd
import numpy as np

import SQLWrapper

# Velos is the name of the server in my file
db =  SQLWrapper.Oracle('DB_NAME')
# note that the limit parameter is database agnostic
df_study = db.select('*', 'TBL_NAME', limit=10) # returns a pandas df
db.read_sql("SELECT COUNT('*') FROM SCHEMA.TBL_NAME")
df_upload.to_sql(
    "table_name", 
    db.engine, 
    schema="schema_name", 
    if_exists='replace', 
    index=False,
    dtype=oracle_dtypes # dictionary of SQLAlchemy DataTypes
)

```

# Notes on Oracle Databases

You must ensure that all your Oracle drivers are setup properly. Refer to these
confluence guides as necessary:
* [How-To](https://confluence.ucdmc.ucdavis.edu/confluence/x/J4swBw): install the full Oracle 19.3c Client drivers using the Admin method to connect to Clarity
* [How-To](https://confluence.ucdmc.ucdavis.edu/confluence/x/_w5QB): connect to Microsoft SQL Server using python and pyodbc
* [How-To](https://confluence.ucdmc.ucdavis.edu/confluence/x/4wxQB): connect to an Oracle Database using python3.6+ and cx_Oracle


Example of `~/.bashrc`

```bash
# Duke's full Oracle 19.3c client env var
# Date: 2021-10-20  
# Oracle Environmental Variables
#----------------------------------
export ORACLE_BASE="/opt/oracle"
export ORACLE_HOME="/opt/oracle/instantclient_19_6"
export LD_LIBRARY_PATH="$ORACLE_HOME/lib:$LD_LIBRARY_PATH"
export TNS_ADMIN="$ORACLE_HOME/network/admin"
export PATH="$ORACLE_HOME/bin:/opt/bin:$PATH"

```

You must also use sqlalchemy datatypes when using `to_sql` to push to an Oracle 
database. See more here: https://docs.sqlalchemy.org/en/14/dialects/oracle.html#oracle-data-types
