#!/usr/bin/env python

import os, sys
import dropboxconnector
import webinterface
import time
import confighandler
import platformutils
import platform
import logging

DB_TOKEN = None
def load_token( pth_token=None ):
    global DB_TOKEN
    DB_TOKEN = confighandler.load_dropboxtoken( pth_token )

USE_GIFPLAYER = (platform.system().lower() != "darwin")
if USE_GIFPLAYER:
    import gifplayer
else:
    import gifplayerosx


def abort( message ):
    sys.stderr.write( message )
    exit(1)


##
# MAIN FLOW
# 

platformutils.init_logging( pth_logfile=confighandler.path_for_resource("log") )

confighandler.load_config()

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

DISPLAY_TIME = 10.0
try:
    while True:

        if DB_TOKEN is None:
            # wait for token to be saved
            pass

        else:
            # token is present
            if dropbox is None:
                logging.info( "init dropbox..." )
                dropbox = dropboxconnector.DropboxConnector( confighandler.pth_root(), "/gifplayer/media", access_token=DB_TOKEN )

            if player is None:
                logging.info( "init player..." )
                if USE_GIFPLAYER:
                    player = gifplayer.GifPlayer()
                    player.init()
                else:
                    player = gifplayerosx.GifPlayerOSX()

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



