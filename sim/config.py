#!/usr/bin/env python

# Sean R. Lang <sean.lang@cs.helsinki.fi>

'''
Configuration options for the code for quick tuning and customizations.
'''

DEBUG = True

DB_ENGINE = 'sqlite:///:memory:'
DB_ECHO = True

DB_POPULATE_SAVE_INTERVAL = 100
DB_UPDATE_SAVE_INTERVAL_AGGPLAYEDHAND = 50
DB_UPDATE_SAVE_INTERVAL_PLAYED_HAND = 50
