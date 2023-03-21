# INSTALLATION
# 00. Installing the module
## A. pipenv
`pipenv install -i 'https://repos.ri.ucdavis.edu' sqlwrapper`

Alternatively, you may edit your Pipefile directly use `pipenv install`
```
################################################################################
# PIPFILE EXAMPLE
################################################################################
[[source]]
name = "pypi"
url = "https://pypi.org/simple"
verify_ssl = true

[[source]]
name = "ripy"
url = "https://repos.ri.ucdavis.edu/python"
verify_ssl = true

[dev-packages]

[packages]
sqlwrapper = {index="ripy", version="*"}
```

## B. PYTHONPATH
```bash
git clone git@github.com:Duke-LeTran/SQLWrapper.git ~/path_to_pythonpath/SQLWrapper
```

Add this line below to your `~/.bashrc` file or alternatively edit your Windows
PYTHONPATH variable.

```bash
export PYTHONPATH="~/path_to_pythonpath/SQLWrapper:$PYTHONPATH"
```

Set up your config files and ensure that the files are permissions protected.
To change from default, edit file `sqlwrapper/config.py`

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