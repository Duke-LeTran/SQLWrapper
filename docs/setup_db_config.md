This file is where you can store all your database connections

# I. SETUP
Set up your config files and ensure that the files are permissions protected.
To change from default, edit file `sqlwrapper/config.py`

##  Where to install this file
1. `Path.home() / '.mypylib / 'db_config.ini'`
2. `Path.cwd() / 'db_config.ini'`

```bash
mkdir ~/.mypylib
cp -r config ~/.mypylib
# rename
mv ~/.mypylib.dbconfig.ini.example ~/.mypylib.dbconfig.ini
# edit your config entries, i.e., db_config.ini
chmod 700 ~/.mypylib/* 
chmod 600 ~/.mypylib/db_config.ini
```

# 01. SETUP: db_config file
Alternatively, you may use vault. To use the local `db_config.ini`, install at
one of the following directories:
* `$HOME/.mypylib/db_config.ini` - useful if you have many db connections
* `$PROJECT_DIR/db_config.ini`

```ini
# I. Oracle
[ORACLE_DB_ENTRY] 
username = dletran
password = fakepw123
db_name = NameOfDatabase
hostname = HostName
service_name = ServiceName
port = 1521

# II. SQL SERVER (windows auth)
[SQLSERVER_DB_ENTRY]
username = dletran
DRIVER = {ODBC Driver 17 for SQL Server}
SERVER = NameOfServer
DATABASE = NameOfDatabase
```


# Parameters
## A. username
* username
* hello (deprecated, but kept for backwards compatability)

## B. password
* password
* world (deprecated, but kept for backwards compatability)

## C. hostname
* hostname
* server

## D. database
* database
* db_name

## E. Other parameters
* port
* driver
* service_name
* tns_alias
