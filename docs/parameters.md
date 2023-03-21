# Parameters
These are a list of paramters can be synonyms.

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

## E. service_name
* service_name
* servicename

## F. Other parameters with no synonyms
* port
* driver
* tns_alias

# Table - Parameters
parameter | Synonym
:----- | :-----
A. username | username, hello (deprecated, but kept for backwards compatability)
B. password | password, world (deprecated, but kept for backwards compatability)
C. hostname | hostname, server
D. database | database, db_name
E. service_name | service_name, servicename
F. Other parameters with no synonyms | port, driver, tns_alias

# Examples
This both fits in the `db_config.ini` file or in vault as a key-pair.
## Oracle
```
[ORACLE_DB_ENTRY] 
username = dletran
password = fakePw123
db_name = nameOfDatabase
hostname = nameOfServer
service_name = serviceName
port = 1521
```
# II. SQL SERVER (windows auth)
```
[SQLSERVER_DB_ENTRY]
username = dletran
DRIVER = {ODBC Driver 17 for SQL Server}
SERVER = nameOfServer
DATABASE = nameOfDatabase
```
