from dropbox import client
import os
import random

class DropboxConnector( object ):

    def __init__( self, pth_root, pth_media, access_token=None ):
        self._pth_root = pth_root
        self._pth_cache = os.path.join( pth_root, "cache" )
        if not os.path.exists( self._pth_cache ):
            os.makedirs( self._pth_cache )
        self._pth_media = pth_media
        self._client = client.DropboxClient( access_token )
    
    def shutdown( self ):
        pass

    def get_nextfile( self ):

        metadata_dir = self._client.metadata( self._pth_media )
        contents = metadata_dir[ "contents" ]

        metadata_file = random.choice( contents )
        pth_file = metadata_file[ "path" ]
        fn = os.path.basename( pth_file )
        pth_cachefile = os.path.join( self._pth_cache, fn )
        
        fh = self._client.get_file( pth_file )
        out = open( pth_cachefile, 'wb' )
        out.write( fh.read() )
        out.close()

        return pth_cachefile

