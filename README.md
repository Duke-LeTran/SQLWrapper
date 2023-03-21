# sqlwrapper

This is a very robust python-SQL database wrapper designed to centralize your
database connections into a single object. It provides pandas-like syntax, and 
an object-oriented experience where all common functions are aggregated into
a single `db` object. This library aims to abstract the complicated formatting 
of connection strings to be database agnostic. The Oracle, SQLServer, and MariaDB 
implementations are the most robust; additional database connections exist 
but may require further development.

# 00. Installation
See ['Installation']('docs/installation.md').

Be sure to complete one of the following setup:
* ['Usage with vault'](docs/setup_db_config.md').
* ['Usage with db_config.ini']('docs/setup_vault.md')


# 01. Quickstart
```python
import pandas as pd
import numpy as np
import sqlwrapper

# Four methods: initalize the database conneciton object
db = sqlwrapper.connect() # this will generate a menu from your db_config file
db = sqlwrapper.connect('ORACLE_DB_ENTRY')
## via vault, assumes .env file is in the current directory
sec_path = 'rifr/ProfilesProd'
db = sqlwrapper.connect(sec_path=sec_path)
```

Then, test your connection with `db.tables()`. This will simply list all the
tables in the database.

At this point, a few things you may use, especially if you're familiar with
`pandas` and `sqlalchemy`:
* `db.read_sql('SELECT * FROM tbl_name')`
* `db.columns('tbl_name')` - returns pandas columns of table
* `db.select('tbl_name', limit=None)` - selects table with no limit; default is 10
* `db.tables()` - returns list of tables
* `db.views()` - returns list of views
* `db.engine` - `sqlalchemy` object engine
* `db.inspector` `sqlalchemy` object inspector

Some additional ideas of usage:

```
with db.engine.connect() as conn:
    conn.execute(query)
```


# 02. Tutorial
# I. DQL
## A. Select
```python
# note, limit flag is databse agnostic
df_upload = db.select('TBL_NAME', limit=None, where='x = y') # returns a pandas df
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

# II. DML
## A. Insert

```python
# uploading df to Oracle database (create table first)
# db.to_oracle(df_upload, 'TBL_NAME') - this is now deprecated
db.insert(df_upload, 'TBL_NAME')
```

This function is crucial for Oracle, which doesn't have `pd.DataFrame.to_sql()` 
with multi flag built. The function uses cx_Oracle's executemany, so it's much 
faster than. Note, the table must already exist in database; db column 
names must match df's cols exactly.

For SQLServer, MySQL, MariaDB, `df.to_sql()` should be sufficient. Future 
functions may wrap around this or the `executemany()` functions.

See more here: 
* https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html


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
# quickly truncate a table of data
db.truncate('API_TABLE', answer='yes')
```

## D. Drop
```python
# drop a table using the db object
db.drop('API_TABLE', answer='yes')
```

# III. Specific Database flavor enhancements

## A. Microsoft SQLServer

Switch database, disposes engine, updates engine, updates object's variables

```python
db.use('COVID_LDS_DLETRAN')

```

## B. Oracle

Not specific, but significiant performance enhancements.

```python
db.insert(df, 'TBL_NAME')
```
## Oracle specific setups

Example of `~/.bashrc`

```bash
# Duke's Oracle 19.3c client env var
# Date: 2021-10-20  
# Oracle Environmental Variables
#----------------------------------
export ORACLE_BASE="/opt/oracle"
export ORACLE_HOME="/opt/oracle/instantclient_19_6" # this may vary for you
export LD_LIBRARY_PATH="$ORACLE_HOME/lib:$LD_LIBRARY_PATH" # this may vary for you
export TNS_ADMIN="$ORACLE_HOME/network/admin"
export PATH="$ORACLE_HOME/bin:$PATH"

```

# IV. Access to SQLAlchemy's objects

If you are familiar with SQLAlchemy, a couple of objects are generated as part 
of the `db` object for convenience if functions are not yet built. This way, 
if you're already familiar with that framework, you have access too.

## A. Engine
```python
# sqlalchemy engine available within object
pd.read_sql('SELECT * FROM TBL_NAME', db.engine)
```

## B. Inspector

For more information on the inspector, see [here](https://docs.sqlalchemy.org/en/14/core/reflection.html#fine-grained-reflection-with-inspector).
```python
db.inspector.get_pk_constraint('TBL_NAME')
db.inspector.get_columns('TBL_NAME')
db.inspector.get_pk_constraint('TBL_NAME')
```

## C. cx_Oracle connections and cursors
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




# 03. Notes to myself

# I. TO-DOs
* add sqlserver.insert() support # executemany
* add mariadb.insert() support # executemany
* add Dockerfile or guide on installing database drivers
* add support for DSN 
* add support for Vault authentication
* add support for `.env` files

# II. Notes on Database drivers

You must ensure that all your Oracle drivers are setup properly. 
* How-To: install the full Oracle 19.3c instantl
* How-To: connect to Microsoft SQL Server using python and pyodbc
* How-To: connect to an Oracle Database using python3.6+ and cx_Oracle

TO-DO: Generate guides or provide Dockerfile