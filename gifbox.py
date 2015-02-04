#!/usr/bin/env python

import sys, os
import dropboxconnector
import webinterface
import time
import morris
import confighandler
import platform

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
    token = None
    if fn_token is None:
        fn_token = pth_token()
    if os.path.exists( fn_token ):
        fh = open( fn_token )
        token = fh.read()
        fh.close()
        if len(token) < 1:
            token = None
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
db_token = load_token()
print "db_token: %s" % db_token
HAS_TOKEN = db_token is not None

# main runloop
dropbox = None
player = None

interface = webinterface.WebInterface( pth_token() )
if not HAS_TOKEN:
    print "no token..."
    def on_token():
        global HAS_TOKEN
        HAS_TOKEN = True
        print "token signal"
    webinterface.token_saved.connect( on_token )
interface.start()

DISPLAY_TIME = 10.0
try:
    while True:

        if not HAS_TOKEN:
            # wait for token to be saved
            pass

        else:
            # token is present
            if dropbox is None:
                print "init dropbox..."
                dropbox = dropboxconnector.DropboxConnector( pth_root(), "/gifplayer/media", access_token=db_token )

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



