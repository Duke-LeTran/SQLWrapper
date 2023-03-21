# Vault
The `.env` is expected to be found in the current project directory.

## .env file
Setup the `.env` file as the following:
```
VAULT_SERVER='https://vault-ri.ucdmc.ucdavis.edu:8200'
VAULT_TOKEN='s.asdfasdfasdfasdfasdfasdf'
```
Be sure to add `.env` to your `.gitignore`.

## Sample usage
```
import sqlwrapper

sec_path='rifr/ProfilesProd'
db = sqlwrapper.connect(sec_path=sec_path)
```
