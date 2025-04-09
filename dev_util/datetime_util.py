# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 10:43:29 2022

@author: kknow

Collection of datetime utilities

"""

import pytz
import datetime as dt
from pytz import timezone
import dateutil.parser as dateparser
import calendar

# TODO Move this to config vars
RPT_TIME_ZONE_TAG = 'America/New_York'
BASE_TZ = pytz.utc
RPT_TZ = pytz.timezone(RPT_TIME_ZONE_TAG)

def get_now():
    """
    Gets the current datetime relative to UTC.

    Parameters
    ----------

    Returns
    -------
    TYPE
        the current datetime relative to UTC.

    """
    
    # https://api.mongodb.com/python/3.4.0/examples/datetimes.html
    # https://gavinwiener.medium.com/quick-tip-converting-python-datetime-timezones-e94d14676ee9
    now = dt.datetime.utcnow().replace(tzinfo=pytz.utc)

    return now

def convert_utc_to_timezone(utc_dt, to_tz=RPT_TZ):
    """
    Converts a UTC datetime to a different timezone (e.g., 'America/New_York')

    Parameters
    ----------
    dt : datetime
        a valid datetime expressed relative to UTC timezone.
    to_tz : TYPE, optional
        timezone for converting from UTC datetime. The default is RPT_TIME_ZONE, which
        is set as a global configuration parameter (e.g., 'America/New_York').

    Returns
    -------
    TYPE
        datetime converted to specified timezone.

    """
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(to_tz)

def get_datetime_as_str(dt, fmt_string="%m/%d/%y %I:%M:%S %p %Z"):
    '''
    Utility method for converting a datetime into a string

    Parameters
    ----------
    dt : TYPE
        DESCRIPTION.
    fmt_string : TYPE, optional
        DESCRIPTION. The default is "%m/%d/%y %I:%M:%S %p %Z".

    Returns
    -------
    dt_str : TYPE
        DESCRIPTION.

    '''

    dt_str = dt.strftime(fmt_string) # + " " + str(update_val.replace(tzinfo=pytz.utc).tzinfo)

    return dt_str
    
def get_utc_as_local_str(utc_dt, fmt_string="%m/%d/%y %I:%M:%S %p %Z"):
    '''
    Utility method for converting a UTC datetime into a local tz string

    Parameters
    ----------
    utc_dt : TYPE
        DESCRIPTION.
    fmt_string : TYPE, optional
        DESCRIPTION. The default is "%m/%d/%y %I:%M:%S %p %Z".

    Returns
    -------
    update_str : TYPE
        DESCRIPTION.

    '''

    local_dt = convert_utc_to_timezone(utc_dt)
    local_dt_str = local_dt.strftime(fmt_string) # + " " + str(update_val.replace(tzinfo=pytz.utc).tzinfo)

    return local_dt_str

def get_datetime_from_timestamp(timestamp):
    '''
    Utility for getting a python datetime from a unix timestamp.  Note that
    the dt returned does not include information about a timezone.

    Parameters
    ----------
    timestamp : TYPE
        DESCRIPTION.

    Returns
    -------
    py_dt : TYPE
        DESCRIPTION.

    '''
    py_dt = dt.datetime.fromtimestamp(timestamp)

    return py_dt

def get_utc_datetime_from_timestamp(timestamp):
    '''
    Utility for getting a python utc datetime from a unix timestamp.  Note that
    the dt returned does not include information about a timezone.

    Parameters
    ----------
    timestamp : TYPE
        DESCRIPTION.

    Returns
    -------
    py_dt : TYPE
        DESCRIPTION.

    '''
    py_dt = dt.datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)

    return py_dt

# https://stackoverflow.com/questions/41726845/convert-zulu-time-string-to-mst-datetime-object
def convert_my_iso_8601(iso_8601, tz_info):
    '''
    Utility function for converting date time strings from UTC to local time

    Parameters
    ----------
    iso_8601 : TYPE
        DESCRIPTION.
    tz_info : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    '''
    assert iso_8601[-1] == 'Z'
    # iso_8601 = iso_8601[:-1] + ':000'
    # iso_8601_dt = dt.datetime.strptime(iso_8601, '%Y-%m-%dT%H:%M:%S.%f')
    iso_8601 = iso_8601[:-1] 
    iso_8601_dt = dt.datetime.strptime(iso_8601, '%Y-%m-%dT%H:%M')
    return iso_8601_dt.replace(tzinfo=timezone('UTC')).astimezone(tz_info)

# TODO Add support for dateparser arguments
def get_datetime_from_datestr(datestr):
    """
    Converts a date string (e.g., "2022-Dec-15") to a datetime.

    Parameters
    ----------
    datestr : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    return dateparser.parse(datestr)

def get_eom_date(date_time):
    
    _, eom_day = calendar.monthrange(date_time.year, date_time.month)
    eom_date = dt.datetime(date_time.year, date_time.month, eom_day)
    
    return eom_date
