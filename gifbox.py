#!/usr/bin/env python

import os, sys, subprocess, shutil
import signal
import dropboxconnector
import webinterface
import time
import confighandler
import platformutils
import logging
from gifplayer import GifPlayer


DB_TOKEN = None
def load_token( pth_token=None ):
    global DB_TOKEN
    DB_TOKEN = confighandler.load_dropboxtoken( pth_token )


def abort( message ):
    sys.stderr.write( message )
    exit(1)

##
# MAIN FLOW
# 

# init logging
platformutils.init_logging(
    pth_logfile=confighandler.path_for_resource("log")
)


# load config
confighandler.load_config()
USE_RAMFS = not confighandler.is_darwin()


# init cache
CACHE_PATH = confighandler.path_for_resource( "cache" )

if os.path.exists( CACHE_PATH ):
    shutil.rmtree( CACHE_PATH )
os.makedirs( CACHE_PATH )

if USE_RAMFS:
    logging.debug( "Use ramfs...")
    args = [ "mount", "-t", "ramfs", "-o", "size=100m", "ramfs", CACHE_PATH ]
    subprocess.call( args )


# load dropbox token
load_token()


# main runloop
dropbox = None
player = None
interface = webinterface.WebInterface()

if not DB_TOKEN:
    logging.info( "no token..." )
    def on_token( pth_token=None ):
        load_token( pth_token )
        logging.info( "token signal" )
    confighandler.token_saved.connect( on_token )
interface.start()

RUNNING = True
def signal_term_handler(signal, frame):
    global RUNNING
    logging.info( 'got SIGTERM' )
    RUNNING = False
signal.signal( signal.SIGTERM, signal_term_handler )

DISPLAY_TIME = 10.0
try:
    while RUNNING:

        if DB_TOKEN is None:
            # wait for token to be saved
            pass

        else:
            # token is present
            if dropbox is None:
                logging.info( "init dropbox..." )
                dropbox = dropboxconnector.DropboxConnector( pth_cache=CACHE_PATH,
                                                                pth_media="/gifplayer/media",
                                                                access_token=DB_TOKEN )

            if player is None:
                player = GifPlayer( cache_path=CACHE_PATH )

            logging.info( "get next gif..." )
            pth_gif = dropbox.get_nextfile()
            logging.info( "-> downloaded %s" % pth_gif )

            player.play( pth_gif )
            
            time.sleep( DISPLAY_TIME )        
            os.remove( pth_gif )
except KeyboardInterrupt:
    pass

# exit main runloop
if player is not None:
    logging.info( "shutdown player")
    player.shutdown()

if dropbox is not None:
    logging.info( "shutdown dropbox")
    dropbox.shutdown()

interface.shutdown()

if USE_RAMFS:
    logging.info( "shutdown ramfs")
    args = [ "umount", CACHE_PATH ]
    subprocess.call( args )

exit(0)

