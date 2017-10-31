import os
import platform
from morris import Signal

DB_TOKEN = None

def is_darwin():
    return platform.system().lower() == "darwin"

def pth_root():
    root = os.path.expanduser( "~/.gifbox" )
    if not os.path.exists( root ):
        os.mkdir( root )
    return root

def path_for_resource( pth_resource ):
    return os.path.join( pth_root(), pth_resource )

def pth_token():
    return path_for_resource( "db_token" )

def load_dropboxtoken( fn_token=None ):
    global DB_TOKEN
    token = None
    if fn_token is None:
        print "get default path"
        fn_token = pth_token()
    print "fn_token: %s" % fn_token
    if os.path.exists( fn_token ):
        fh = open( fn_token )
        token = fh.read().rstrip()
        fh.close()
        if len(token) < 1:
            token = None
    DB_TOKEN = token
    return token

def dropbox_token():
    global DB_TOKEN
    if DB_TOKEN is None:
        load_dropboxtoken()
    return DB_TOKEN

@Signal.define
def token_saved( pth_token ):
    pass

def save_token( self, token ):
        fn_token = pth_token()
        fh = open( fn_token, "w" )
        fh.write( token )
        fh.close()
        token_saved( fn_token )

def load_config():
    fh = open( path_for_resource( ".env" ) )
    lines = fh.readlines()
    fh.close()

    for line in lines:
        line = line.rstrip()
        key, val = line.split( "=" )
        os.environ[ key ] = val 
