#!/usr/bin/env python

import sys, os
import dropboxconnector
import webinterface
import time
import morris
import confighandler
import platform

DB_TOKEN = None
USE_GIFPLAYER = (platform.system().lower() != "darwin")
if USE_GIFPLAYER:
    import gifplayer
else:
    import gifplayerosx

def pth_root():
    root = os.path.expanduser( "~/.gifbox" )
    if not os.path.exists( root ):
        os.mkdir( root )
    return root

def pth_token():
    return os.path.join( pth_root(), "db_token" )

def load_token( fn_token=None ):
    global DB_TOKEN
    token = None
    if fn_token is None:
        fn_token = pth_token()
    if os.path.exists( fn_token ):
        fh = open( fn_token )
        token = fh.read()
        fh.close()
        if len(token) < 1:
            token = None
    DB_TOKEN = token
    return token

def abort( message ):
    sys.stderr.write( "No Dropbox token found. Set one in the web interface before running gifbox." )
    exit(1)

##
# MAIN FLOW
# 

confighandler.load_config()

# gifbox's working dir

# load dropbox token
load_token()

# main runloop
dropbox = None
player = None

interface = webinterface.WebInterface( pth_token() )
if not DB_TOKEN:
    print "no token..."
    def on_token( pth_token=None ):
        self.load_token( pth_token )
        print "token signal"
    webinterface.token_saved.connect( on_token )
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
                print "init dropbox..."
                dropbox = dropboxconnector.DropboxConnector( pth_root(), "/gifplayer/media", access_token=DB_TOKEN )

            if player is None:
                print "init player..."  
                if USE_GIFPLAYER:
                    player = gifplayer.GifPlayer()
                    player.init()
                else:
                    player = gifplayerosx.GifPlayerOSX()

            print "get next gif..."
            pth_gif = dropbox.get_nextfile()
            print pth_gif

            player.play( pth_gif )
            
            time.sleep( DISPLAY_TIME )        
            os.remove( pth_gif )
except KeyboardInterrupt:
    pass

# exit main runloop
if player is not None:
    player.shutdown()

if dropbox is not None:
    dropbox.shutdown()

interface.shutdown()



