#!/usr/bin/env python

# Sean R. Lang <sean.lang@cs.helsinki.fi>

'''
Configuration options for the code for quick tuning and customizations.
'''

DEBUG = True

if DEBUG:
    DB_ENGINE = 'sqlite:///:memory:'
    DB_ECHO = False #True

    DB_POPULATE_SAVE_INTERVAL = 10
    DB_UPDATE_SAVE_INTERVAL_AGGPLAYEDHAND = 5
    DB_UPDATE_SAVE_INTERVAL_PLAYED_HAND = 5

    DB_AGG_REC_REFRESH_MODULO = 128
else:
    DB_ENGINE = 'sqlite:///:memory:'
    DB_ECHO = False

    DB_POPULATE_SAVE_INTERVAL = 100
    DB_UPDATE_SAVE_INTERVAL_AGGPLAYEDHAND = 50
    DB_UPDATE_SAVE_INTERVAL_PLAYED_HAND = 50

    DB_AGG_REC_REFRESH_MODULO = 128
