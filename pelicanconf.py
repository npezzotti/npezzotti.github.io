# Basic Settings
USE_FOLDER_AS_CATEGORY = True
DELETE_OUTPUT_DIRECTORY = True
DEFAULT_CATEGORY = 'misc'
DISPLAY_PAGES_ON_MENU = True
DISPLAY_CATEGORIES_ON_MENU = False
AUTHOR = 'Nathan Pezzotti'
RELATIVE_URLS = True
OUTPUT_PATH = 'output/'
PATH = 'content'
ARTICLE_PATHS = ['blog']
SITENAME = 'Nathan\'s Blog'
SITEURL = 'https://npezzotti.github.io'
PORT = 8000
BIND = '127.0.0.1'
STATIC_PATHS = ['images']

PATH = 'content'
TIMEZONE = 'America/New_York'
DEFAULT_LANG = 'en'

# Feed Settings
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

SUMMARY_MAX_LENGTH = 10

DEFAULT_PAGINATION = 10

# Translation

# Ordering Content
ARTICLE_ORDER_BY = 'date'

# Themes
THEME = 'themes/npezzotti-theme'
SOCIAL = (
    ('github', 'https://github.com/npezzotti'),
    ('email', 'npezzotti80@gmail.com'),
)
MENUITEMS = (('Home', '/'), ('Posts', '/categories'))
GITHUB_URL = "https://github.com/npezzotti"
