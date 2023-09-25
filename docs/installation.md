# INSTALLATION
# 00. Installing the module

## A. pip
The package is available on UCDH intranet, so you may use pip.

### Install in one command
`pip install -i https://repos.ri.ucdavis.edu/python --extra-index-url https://pypi.org/simple sqlwrapper`

### Install dependecies separately
Install dependencies first: 
`pip install pandas pyodbc cx-oracle sqlalchemy python-dotenv hvac openpyxl` 

Then use one of the following:
* `pip install -i 'https://repos.ri.ucdavis.edu/python' sqlwrapper`
* `pip install --index-url 'https://repos.ri.ucdavis.edu/python' sqlwrapper`
* `pip install --extra-index 'https://repos.ri.ucdavis.edu/python' sqlwrapper`

Using `virtualenv` or `venv`. More on python virtual environments [here](https://realpython.com/python-virtual-environments-a-primer/).

```
> python -m venv vsql # alternatively: virtualenv vsql
> source sqlvenv/bin/activate
> (sqlvenv) pip install sqlalchemy cx-oracle pyodbc numpy pandas
> (sqlvenv) pip install -i 'https://repos.ri.ucdavis.edu/python' sqlwrapper
```

## B. pipenv
`pipenv install -i 'https://repos.ri.ucdavis.edu' sqlwrapper`

Alternatively, you may edit your Pipefile directly, then use `pipenv install`.
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
#sqlwrapper = {editable = true, git = "https://github.com/Duke-LeTran/SQLWrapper"}
piesafe = {index="ripy", version="*"}
ucd-ri-pydbutils = {index="ripy", version="*"}
pandas = "*"
numpy = "*"
requests = "*"
sqlalchemy = "*"
openpyxl = "*"
hvac = "*"
python-dotenv = "*"
cx-oracle = "*"
pyodbc = "*"
pymysql = "*"
```

## C. PYTHONPATH
You may clone down the repository and add it to your `PYTHONPATH`.

```bash
git clone git@github.com:Duke-LeTran/SQLWrapper.git ~/path_to_pythonpath/SQLWrapper
```

Add this line below to your `~/.bashrc` file

Similarly on Windows, edit your Windows  variable:
`Start > Edit environment variables for your account > Path:Edit > New`

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

Note that sqlwrapper will search for the `db_config.ini` file in two directories 
in this order: 
1. `Path.home() / Path('.mypylib')`
2. `Path.cwd()`

# 01. SETUP: db_config file
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


# III. Mariadb
[MyProfiles]
username=dletran
password=fakepw123
hostname=servername.ucdmc.ucdavis.edu
port=3306
db_name=NameOfDatabase
db_type=MariaDB
```