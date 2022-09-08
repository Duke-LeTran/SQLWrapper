# SQLWrapper

This is a very robust python-SQL database wrapper designed to centralize your
database connections into a single object. It is desiged to abstract the
complicated formatting of DSN connection strings. The Oracle and SQLServer 
implementations are the most robust. Additional database connections exist but
may require further development.

# Setup
```bash
git clone git@github.com:Duke-LeTran/SQLWrapper.git ~/path_to_pythonpath/SQLWrapper
```

Add this line below to your `~/.bashrc` file.

```bash
export PYTHONPATH="~/path_to_pythonpath/SQLWrapper:$PYTHONPATH"
```

Set up your config files and ensure that the files are permissions protected.
To change from default, edit file `SQLWrapper/config.py`

```bash
cp -r config ~/.mypylib
# edit your config files, i.e., db_config.ini
chmod 600 ~/.mypylib/* 
```

Now you should be able to import SQLWrapper from anywhere.
        
# Sample setup of config file 
This is your config file. Entries will need to be edited to reflect your 
personal databases. See a few example entries below. My prefered location to 
place this file is: `$HOME/.mypylib/db_config.ini`

```ini
# I. Oracle
[ORACLE_DB_ENTRY] 
hello = dletran
world = fakepw123
db_name = NameOfDatabase
hostname = HostName
service_name = ServiceName
port = 1521

# II. SQL SERVER (windows auth)
[SQLSERVER_DB_ENTRY]
hello = dletran
DRIVER = {ODBC Driver 17 for SQL Server}
SERVER = NameOfServer
DATABASE = NameOfDatabase
```


# Sample use

## Connect
```python
import pandas as pd
import numpy as np
import SQLWrapper
from sqlalchemy.dialects.oracle import NUMBER, VARCHAR2, DATE

# Initalize the database conneciton object
db =  SQLWrapper.Oracle('ORACLE_DB_ENTRY')
# note that the limit parameter is database agnostic
```

## Select
```python
df_upload = db.select('TBL_NAME', limit=None) # returns a pandas df
db.read_sql("SELECT COUNT('*') FROM SCHEMA.TBL_NAME") # similar to pd.read_sql()

# generates a sqlalchemy engine, based on your config file
pd.read_sql('SELECT * FROM TBL_NAME', db.engine)
```

## Database inspection: Tables
```python
# db-agnostic, returns list of all tables of connected database
db.tables()

```

## Database inspection: Columns
```python
# columns - returns pandas index of columns
db.columns('TBL_NAME')
# columns - verbose flag
db.columns('TBL_NAME', verbose=True)
```

## Insert

### Oracle
```python
# uploading df to Oracle database (create table first)
db.to_oracle(df_upload, db.schema_name, 'TBL_NAME', db.engine)
```


## Other
```python
# if you need a cx_Oracle connection
conn = db.engine.raw_connection()
conn.close()

# switch database, disposes engine, updates engine, updates object's variables
db.use_db('COVID_LDS_DLETRAN')

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
export ORACLE_HOME="/opt/oracle/instantclient_19_6" # this may vary for you
export LD_LIBRARY_PATH="$ORACLE_HOME/lib:$LD_LIBRARY_PATH" # this may vary for you
export TNS_ADMIN="$ORACLE_HOME/network/admin"
export PATH="$ORACLE_HOME/bin:$PATH"

```

You must also use sqlalchemy datatypes when using `pd.df.to_sql()` to push to an
Oracle database. 

See more here: 
* https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html
* https://docs.sqlalchemy.org/en/14/dialects/oracle.html#oracle-data-types