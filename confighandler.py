import os

def load_config():
    this_dir = os.path.realpath( os.path.dirname(__file__) )
    fh = open( os.path.join( this_dir, ".env" ) )
    lines = fh.readlines()
    fh.close()

    for line in lines:
        line = line.rstrip()
        key, val = line.split( "=" )
        os.environ[ key ] = val 
