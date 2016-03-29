"""Settings file - will load data from (private) local settings"""

# dummy data
WEB_CLIENT_ID = 'replace with Web client ID'
ANDROID_CLIENT_ID = 'replace with Android client ID'
IOS_CLIENT_ID = 'replace with iOS client ID'
ANDROID_AUDIENCE = WEB_CLIENT_ID

# load from local settings file (if exists)
try:
    from local_settings import *
except ImportError:
    pass
