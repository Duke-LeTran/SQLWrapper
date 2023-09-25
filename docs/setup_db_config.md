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

# II. SETUP: db_config file
Alternatively, you may use vault. To use the local `db_config.ini`, install at
one of the following directories:
* `$HOME/.mypylib/db_config.ini` - useful if you have many db connections
* `$PROJECT_DIR/db_config.ini`

Here are some sample entries:
```ini
# I. Oracle
[ORACLE_DB_ENTRY] 
username = dletran
password = fakepw123
db_name = NameOfDatabase
hostname = HostName
service_name = ServiceName
port = 1521

# II. SQL SERVER
[SQLSERVER_WindowsAuth]
username = dletran
DRIVER = {ODBC Driver 17 for SQL Server}
SERVER = NameOfServer
DATABASE = NameOfDatabase

[SQLSERVER_FreeTDS]
hello=HS\\dletran
DRIVER={FreeTDS}
SERVER=NameOfServer
DATABASE=NameOfDatabase
db_type=SQLServer

[SQLSERVER_service_account]
username=srv-username
password=fakepw123
DRIVER={ODBC Driver 17 for SQL Server}
SERVER=HSSERVERNAME
DATABASE=NameOfDatabase
db_type=SQLServer


# III. Mariadb
[MyProfiles]
username=dletran
password=fakepw123
hostname=servername.ucdmc.ucdavis.edu
port=3306
db_name=NameOfDatabase
db_type=MariaDB
```