# sqlwrapper

This is a very robust python-SQL database wrapper designed to centralize your
database connections into a single object. It provides pandas-like syntax, and 
an object-oriented experience where all common functions are aggregated into
a single `db` object. This library aims to abstract the complicated formatting 
of DSN connection strings to be database agnostic. The Oracle, SQLServer, and MariaDB 
implementations are the most robust; additional database connections exist 
but may require further development.

# 00. Setup
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
        
# 01. Sample setup of config file 
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


# 02. Tutorial

## A. Connect and initialize
```python
import pandas as pd
import numpy as np
import SQLWrapper
from sqlalchemy.dialects.oracle import NUMBER, VARCHAR2, DATE

# Initalize the database conneciton object
db =  SQLWrapper.Oracle('ORACLE_DB_ENTRY')
# note that the limit parameter is database agnostic
```

## B. Common SQLAlchemy objects

If you are familiar with SQLAlchemy, a couple of objects are generated as part 
of the `db` object for convenience. This way, if you're already familiar with
that framework, this something you may want to use.

### Engine
```python
# sqlalchemy engine available within object
pd.read_sql('SELECT * FROM TBL_NAME', db.engine)
```

### Inspector

For more information on the inspector, see [here](https://docs.sqlalchemy.org/en/14/core/reflection.html#fine-grained-reflection-with-inspector).
```python
db.inspector.get_pk_constraint('TBL_NAME')
db.inspector.get_columns('TBL_NAME')
db.inspector.get_pk_constraint('TBL_NAME')
```

### cx_Oracle connections and cursors
```python
# if you need a cx_Oracle connection
conn, cursor = db._generate_conn_cursor()

try:
    cursor.execute('')
    conn.commit()
except Exception as e:
    log.error(e)
finally:
    conn.close()
    cursor.close()
```

# 03. DQL
## A. Select
```python
df_upload = db.select('TBL_NAME', limit=None, where='WHERE x = y') # returns a pandas df
```

## B. Database inspection: Tables
```python
# db-agnostic, returns list of all tables of connected database
db.tables()

```

## C. Database inspection: Views
```python
# db-agnostic, returns list of all views of connected database
db.views()

```

## Database inspection: Columns
```python
# columns - returns pandas index of columns
db.columns('TBL_NAME')
# columns - verbose flag
db.columns('TBL_NAME', verbose=True)
```

# III. DML
## A. Insert

Note, table must already exist in database; db column names must match df's cols exactly.

```python
# uploading df to Oracle database (create table first)
# db.to_oracle(df_upload, 'TBL_NAME') - this is now deprecated
db.insert(df_upload, 'TBL_NAME')
```

## B. Update

Using a for loop, this function can help automate writing the `UPDATE` statements.

```python
for idx, row in df.iterrows():
    #db.update('tbl_name', 'set_col', 'set_val', 'cond_col', 'condition')
    db.update('MAPPED_TITLE', #tbl_name
                'TM_COHORT', #set_col
                f"'{row['TM_COHORT']}'", #set_value
                'TITLECODE', #conditional_column
                f"'{str(row['TITLECODE']).rjust(6,'0')}'", #condition
                autocommit=True)

    # This will print and execute the following code:
    ## UPDATE MAPPED_TITLE 
    ## SET TM_COHORT = {set_value} 
    ## WHERE TITLECODE = '000136';
```
## C. Truncate
```python
# quickly trucnate a table of data
db.truncate('API_TABLE', answer='yes')
```

## D. Drop
```python
# drop a table using the db object
db.drop('API_TABLE', answer='yes')
```

# IV. Other tools

This are miscellaneous functions that may also be useful

## A. Switch between schemas

Switch database, disposes engine, updates engine, updates object's variables

```python
db.use_db('COVID_LDS_DLETRAN')

```

# V. Notes on Oracle Databases

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
