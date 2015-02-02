import os

def load_config():
    this_dir = os.path.realpath( os.path.dirname(__file__) )
    fh = open( os.path.join( this_dir, ".env" ) )
    lines = fh.readlines()
    fh.close()

    for line in lines:
        key, val = line.split( "=" )
        os.environ[ key ] = val 