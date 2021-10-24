# SQLWrapper

This is a very robust python-SQL database wrapper designed to centralize your
database connections into a single object. It is desiged to abstract the
complicated formatting of DSN connection strings. The Oracle implementation is
thoroughly tested, but the Microsoft SQL Server still needs further development.

# Setup
```bash
git clone git@github.com:Duke-LeTran/SQLWrapper.git ~/path_to_pythonpath/SQLWrapper
```

Add this `~/.bashrc` file.

```bash
export PYTHONPATH="~/path_to_pythonpath/SQLWrapper"
```

Set up your config files and ensure it is permissions protected.

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
[SQLServerDbAlias]
hello = dletran
DRIVER = {ODBC Driver 17 for SQL Server}
SERVER = NameOfServer
DATABASE = NameOfDatabase
```


# Sample use

```python
import pandas as pd
import numpy as np
import SQLWrapper

# Velos is the name of the server in my file
db =  SQLWrapper.Oracle('ORACLE_DB_ENTRY')
# note that the limit parameter is database agnostic
df_study = db.select('*', 'TBL_NAME', limit=10) # returns a pandas df
db.read_sql("SELECT COUNT('*') FROM SCHEMA.TBL_NAME")

oracle_dtypes = {
            'col_integer' : NUMBER(38,0),
            'col_string' : VARCHAR2(50),
            'col_date' : DATE()
}

#
df_upload.to_sql(
    "table_name", 
    db.engine, 
    schema="schema_name", 
    if_exists='replace', 
    index=False,
    dtype=oracle_dtypes # dictionary of SQLAlchemy DataTypes
)
# if you need a cx_Oracle connection
conn = db.engine.raw_connection()

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

You must also use sqlalchemy datatypes when using `pd.df.to_sql()` to push to an Oracle 
database. 
See more here: 
* https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html
* https://docs.sqlalchemy.org/en/14/dialects/oracle.html#oracle-data-types
