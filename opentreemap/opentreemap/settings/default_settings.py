import os
from omgeo import postprocessors

# Django settings for opentreemap project.
OTM_VERSION = 'dev'
API_VERSION = 'v0.1'

FEATURE_BACKEND_FUNCTION = None
USER_ACTIVATION_FUNCTION = None
INSTANCE_PERMISSIONS_FUNCTION = 'treemap.instance.get_instance_permission_spec'

ECOSERVICE_NAME = 'otm-ecoservice'

UITEST_CREATE_INSTANCE_FUNCTION = 'treemap.tests.make_instance'
UITEST_SETUP_FUNCTION = None

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# This email is shown in various contact/error pages throughout the site
SUPPORT_EMAIL_ADDRESS = 'support@yoursite.com'
# This email is used as the "from" address when sending messages
DEFAULT_FROM_EMAIL = 'noreply@yoursite.com'
SYSTEM_USER_ID = -1

#
# URL to access eco benefit service
#
ECO_SERVICE_URL = 'http://localhost:13000'

# This should be the google analytics id without
# the 'GTM-' prefix
GOOGLE_ANALYTICS_ID = None

# Tree Key URL to use for help links of an instance doesn't provide
# one
DEFAULT_TREE_KEY_URL = 'http://www.arborday.org/trees/whatTree/'

# Storage backend config
# Uncomment the following to enable S3-backed storage:
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
# AWS_ACCESS_KEY_ID = '...'
# AWS_SECRET_ACCESS_KEY = '...'
# AWS_STORAGE_BUCKET_NAME = '...'
AWS_HEADERS = {
    'Cache-Control': 'max-age=86400',
}

# Size is in bytes (20 MB)
MAXIMUM_IMAGE_SIZE = int(os.environ.get('DJANGO_MAXIMUM_IMAGE_SIZE', 20971520))
MAXIMUM_IMAGE_SIZE_MB = MAXIMUM_IMAGE_SIZE / 1024 / 1024

# API distance check, in meters
MAP_CLICK_RADIUS = 100
# API instance distance default, in meters
NEARBY_INSTANCE_RADIUS = 100000

# Default nearby tree distance in meters
NEARBY_TREE_DISTANCE = 6.096  # 20ft

DEBUG = True
AUTH_USER_MODEL = 'treemap.User'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.AllowAllUsersModelBackend']
INTERNAL_IPS = ['127.0.0.1']
ALLOWED_HOSTS = ['localhost']

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

TEST_RUNNER = "treemap.tests.OTM2TestRunner"

OMGEO_SETTINGS = [[
    'omgeo.services.EsriWGS',
    {
        'preprocessors': [],
        'postprocessors': [
            postprocessors.UseHighScoreIfAtLeast(99),
            postprocessors.DupePicker(  # Filters by highest score
                attr_dupes='match_addr',
                attr_sort='locator_type',
                ordered_list=['PointAddress', 'BuildingName', 'StreetAddress']
            ),
            postprocessors.GroupBy('match_addr'),
            postprocessors.GroupBy(('x', 'y')),
            postprocessors.SnapPoints(distance=10)],
        'settings': {
            'client_id': os.environ.get('ESRI_CLIENT_ID'),
            'client_secret': os.environ.get('ESRI_CLIENT_SECRET')
        }
    }
]]

# Set TILE_HOST to None if the tiler is running on the same host
# as this app. Otherwise, provide a Leaflet url template as described
# at http://leafletjs.com/reference.html#url-template
#
# Tile hosts must be serving tiles on a 'tile' endpoint
#
#   //host/tile/
#
TILE_HOST = None

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Setting this to False will remove the jsi18n url configuration
USE_JS_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True
USE_THOUSAND_SEPARATOR = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Path to the Django Project root
# Current file is in opentreemap/opentreemap/settings, so go up 3
BASE_DIR = os.path.abspath(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Path to the Repository root
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Path to the location of SCSS files, used for on-the-fly compilation to CSS
SCSS_ROOT = os.path.join(PROJECT_ROOT, 'assets', 'css', 'sass')

# Entry point .scss file for on-the-fly compilation to CSS
SCSS_ENTRY = 'main'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = '/usr/local/otm/media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"

# TODO: Media serving via ansible
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
WEBPACK_DEV_SERVER = os.environ.get('WEBPACK_DEV_SERVER', None)

if WEBPACK_DEV_SERVER is not None and DEBUG:
    STATIC_URL = WEBPACK_DEV_SERVER + 'static/'
else:
    STATIC_URL = '/static/'

# Root URL for the application
SITE_ROOT = '/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Webpack compiled files are output here
    os.path.join(PROJECT_ROOT, 'static/'),
    # This is the directory where webpack gets its source data from
    # We use this as a static directory so that images can be referenced in CSS
    # but also be collected by collectstatic
    os.path.join(PROJECT_ROOT, 'assets/'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'secret key'

# Settings for Django Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'opentreemap.context_processors.global_settings',
            ],
            'loaders': [
                'django.template.loaders.app_directories.Loader',
                'apptemplates.Loader'
            ],
        },
    },
]

MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'opentreemap.middleware.InternetExplorerRedirectMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# Settings for Rollbar exception reporting service
ROLLBAR_SERVER_ACCESS_TOKEN = os.environ.get(
    'ROLLBAR_SERVER_SIDE_ACCESS_TOKEN', None)
ROLLBAR_CLIENT_ACCESS_TOKEN = os.environ.get(
    'ROLLBAR_POST_CLIENT_ITEM_ACCESS_TOKEN', None)
STACK_TYPE = os.environ.get('OTM_STACK_TYPE', 'Unknown')
if ROLLBAR_SERVER_ACCESS_TOKEN is not None:
    ROLLBAR = {
        'access_token': ROLLBAR_SERVER_ACCESS_TOKEN,
        'environment': STACK_TYPE,
        'root': BASE_DIR
    }
    MIDDLEWARE += (
        'rollbar.contrib.django.middleware.RollbarNotifierMiddleware',)

STACK_COLOR = os.environ.get('OTM_STACK_COLOR', 'Black')

CELERY_TASK_DEFAULT_QUEUE = STACK_COLOR
CELERY_TASK_DEFAULT_ROUTING_KEY = "task.%s" % STACK_COLOR
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_ACCEPT_CONTENT = ['pickle', 'application/json']

ROOT_URLCONF = 'opentreemap.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'opentreemap.wsgi.application'

COMMENTS_APP = 'otm_comments'

# Necessary to prevent the underlying `django_comments` app
# from hiding all comments with `is_removed` set to true.
# We want to show these comments, with details masked to
# indicate that they were "hidden" by a moderator.
COMMENTS_HIDE_REMOVED = False

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.auth',
    'captcha',
    'treemap',
    'geocode',
    'api',
    'exporter',
    'otm1_migrator',
    'threadedcomments',
    'django_comments',
    'otm_comments',
    'importer',
    'appevents',
    'stormwater',
    'manage_treemap',
    'modeling',
    'registration',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.gis',
    'django.contrib.humanize',
    'django.contrib.postgres',
    'django_js_reverse',
    'webpack_loader',
    'frontend',
)

I18N_APPS = (
    'treemap',
)

RESERVED_INSTANCE_URL_NAMES = (
    'geocode',
    'config',
    'users',
    'api',
    'accounts',
    'i18n',
    'not-available',
    'unsupported',
    'jsi18n',
    'admin'
)

# From the django-registration quickstart
# https://django-registration.readthedocs.org/en/latest/quickstart.html
#
# ACCOUNT_ACTIVATION_DAYS is the number of days users will have to activate
# their accounts after registering. If a user does not activate within
# that period, the account will remain permanently inactive and
# may be deleted by maintenance scripts provided in django-registration.
ACCOUNT_ACTIVATION_DAYS = 7

# Django-registration-redux sends HTML emails by default as of version 1.2
# Disabling them for now until we add some new email templates
REGISTRATION_EMAIL_HTML = False

#
# Units and decimal digits for fields and eco values
#
# DISPLAY_DEFAULTS has the default unit to show in the UI
# STORAGE_UNITS is the unit the value will be stored/computed as,
# if different from DISPLAY_DEFAULTS
#
STORAGE_UNITS = {
    'greenInfrastructure': {
        'area': 'sq_m'
    }
}
DISPLAY_DEFAULTS = {
    'plot': {
        'width':  {'units': 'in', 'digits': 1},
        'length': {'units': 'in', 'digits': 1},
    },
    'tree': {
        'diameter':      {'units': 'in', 'digits': 1},
        'height':        {'units': 'ft', 'digits': 1},
        'canopy_height': {'units': 'ft', 'digits': 1}
    },
    'eco': {
        'energy':     {'units': 'kwh/year', 'digits': 1},
        'stormwater': {'units': 'gal/year', 'digits': 1},
        'co2':        {'units': 'lbs/year', 'digits': 1},
        'co2storage': {'units': 'lbs', 'digits': 1},
        'airquality': {'units': 'lbs/year', 'digits': 1}
    },
    'bioswale': {
        'drainage_area': {'units': 'sq_ft', 'digits': 1}
    },
    'rainBarrel': {
        'capacity': {'units': 'gal', 'digits': 1}
    },
    'rainGarden': {
        'drainage_area': {'units': 'sq_ft', 'digits': 1}
    },
    'greenInfrastructure': {
        'rainfall': {'units': 'in', 'digits': 1},
        'area':     {'units': 'sq_ft', 'digits': 1}
    }
}

# Time in ms for two clicks to be considered a double-click in some scenarios
DOUBLE_CLICK_INTERVAL = 300

# The number of plots to import per task
IMPORT_BATCH_SIZE = 85

# The rate limit for how frequently batches of imports can happen per worker
IMPORT_COMMIT_RATE_LIMIT = "1/m"

IE_VERSION_MINIMUM = 11

IE_VERSION_UNSUPPORTED_REDIRECT_PATH = '/unsupported'

USE_OBJECT_CACHES = True
USE_ECO_CACHE = True

BING_API_KEY = None
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_KEY', None)

JS_REVERSE_JS_MINIFY = False
JS_REVERSE_OUTPUT_PATH = os.path.join(PROJECT_ROOT, 'assets/js/shim')

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': '/',  # must end with slash
        'STATS_FILE': os.path.join(PROJECT_ROOT, 'static',
                                   'webpack-stats.json')
    }
}

# For django-recaptcha https://github.com/praekelt/django-recaptcha
# Setting NOCAPTCHA to True enables v2
NOCAPTCHA = True

if os.environ.get('RECAPTCHA_PUBLIC_KEY', '') != '':
    # We use an if block here because django-recaptcha will only use a default
    # test key if these settings are undefined.
    RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY', None)
    RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY', None)
    USE_RECAPTCHA = True
else:
    USE_RECAPTCHA = False


DEFAULT_INSTANCE = 'JerseyCity'

INATURALIST_URL = ''

CORS_ORIGIN_WHITELIST = (
    'http://localhost:3000',
    'http://localhost:8080'
)
