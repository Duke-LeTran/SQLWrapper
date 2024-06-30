from sqlwrapper.errors import Missing_DBCONFIG_ValueError

class parameters:
    """
    For db_config parameter backwards compatability and data interoperability.
    Nomralizes the varying parameter synonyms.

    These functions help collate synonyms that represent the same concept, e.g..
        * [username, hello]
        * [password, pw, world]
        * [server, hostname]
    """
    def __init__(self):
        pass

    @property
    def _username(self):
        result = self._config.get('username', self._config.get('hello'))
        if result is None:
            raise Missing_DBCONFIG_ValueError# Error
        else:
            return result
    
    @property
    def _pw(self):
        result = self._config.get('password', self._config.get('world'))
        if result is None:
            raise Missing_DBCONFIG_ValueError# Error
        else:
            return result

    @property
    def _hostname(self):
        result = self._config.get('server', self._config.get('hostname'))
        if result is None:
            raise Missing_DBCONFIG_ValueError# Error
        else:
            return result
    
    @property
    def _database(self):
        result = self._config.get('database', self._config.get('db_name'))
        if result is None:
            raise Missing_DBCONFIG_ValueError# Error
        else:
            return result
    
    @property
    def _port(self):
        result = self._config.get('port')
        if result is None:
            raise Missing_DBCONFIG_ValueError# Error
        else:
            return result
    
    @property
    def _driver(self):
        result = self._config.get('driver')
        if result is None:
            raise Missing_DBCONFIG_ValueError# Error
        else:
            return result
    
    @property
    def _service_name(self):
        result = self._config.get('service_name', self._config.get('servicename'))
        if result is None:
            raise Missing_DBCONFIG_ValueError# Error
        else:
            return result
        
    @property
    def _tns_alias(self):
        result = self._config.get('tns_alias')
        if result is None:
            raise Missing_DBCONFIG_ValueError# Error
        else:
            return result
    