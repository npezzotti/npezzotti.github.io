# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *

# Basic Settings
USE_FOLDER_AS_CATEGORY = True
DELETE_OUTPUT_DIRECTORY = True
DEFAULT_CATEGORY = 'misc'
DISPLAY_PAGES_ON_MENU = True
DISPLAY_CATEGORIES_ON_MENU = False
SITENAME = 'Nathan\'s Blog'
SITEURL = 'npezzotti.github.io'
RELATIVE_URLS = False
OUTPUT_PATH = 'output/'
PATH = 'content'
ARTICLE_PATHS = ['blog']
STATIC_PATHS = ['images']

# URL Settings

# Time and Date
FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/{slug}.atom.xml'

# Template Pages

# Metadata

# Feed Settings

# Pagination
DELETE_OUTPUT_DIRECTORY = True
DEFAULT_PAGINATION = 10

# Translation

# Ordering Content
ARTICLE_ORDER_BY = 'date'

# Themes
THEME = 'themes/npezzotti-theme'
SOCIAL = (
    ('github', 'https://www.github.com/npezzotti'),
    ('email', 'npezzotti80@gmail.com'),
    ('linkedin', 'https://www.linkedin.com/in/nathan-pezzotti/')
)
MENUITEMS = (('Home', '/'), ('Posts', '/posts'),)
GITHUB_URL = "https://www.github.com/npezzotti"
