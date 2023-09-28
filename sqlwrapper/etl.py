"""
This provides a user timer decorator for ETL process functions.

Duke LeTran <daletran@ucdavis.edu>
Research Infrastructure, IT Health Informatics, UC Davis Health
Copyright 2022, UC Regents
"""
import logging
import functools
import time

log = logging.getLogger(__name__)

def convert_time(time_elapsed) -> tuple:
    hrs = time_elapsed // 3600
    mins = (time_elapsed % 3600) // 60
    secs = (time_elapsed % 3600) % 60
    return hrs, mins, secs


"""
This provides a user timer decorator for ETL process functions.

Duke LeTran <daletran@ucdavis.edu>
Research Infrastructure, IT Health Informatics, UC Davis Health
Copyright 2022, UC Regents
"""
import logging
import functools
import time

log = logging.getLogger(__name__)

def convert_time(time_elapsed) -> tuple:
    hrs = time_elapsed // 3600
    mins = (time_elapsed % 3600) // 60
    secs = (time_elapsed % 3600) % 60
    return hrs, mins, secs


def timer(func):
    """
     Decorator Practice - Prints the runtime of the decorated function
    * https://betterprogramming.pub/decorators-in-python-72a1d578eac4
    * https://realpython.com/primer-on-python-decorators/#timing-functions
    * https://realpython.com/primer-on-python-decorators/#decorators-with-arguments
    """
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter() # starts counting
        output = func(*args, **kwargs) # main
        end_time = time.perf_counter() # ends counting
        time_elapsed = end_time - start_time
        hrs, mins, secs = convert_time(time_elapsed)
        log.debug(f"DEBUG: ETL process completed in raw {time_elapsed:.4f}s.")
        if time_elapsed < 60: # if seconds
            log.info(f"ETL process [{func.__module__}.{func.__name__}()] completed in {time_elapsed:.4f}s.")
        elif (time_elapsed >= 60) and (time_elapsed < 3600): # if minutes
            log.info(f"ETL process [{func.__module__}.{func.__name__}()] completed in {mins} min(s) and {secs:.2f}s.")
        elif time_elapsed >= 3600: # if hours
            log.info(f"ETL process [{func.__module__}.{func.__name__}()] completed in {hrs} hr(s), {mins} min(s) and {secs:.1f}s..")
        return output
    return wrapper_timer