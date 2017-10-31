import logging


class GifPlayer():


    def __init__( self, cache_path=None, use_pygame=False ):
        
        logging.info( "init GifPlayer..." )

        if use_pygame :
            import gifplayerpygame
            self._player = gifplayerpygame.GifPlayer(
                pth_cache = cache_path
            )
            self._player.init()
        
        else:
            import gifplayerosx
            self._player = gifplayerosx.GifPlayerOSX()


    def play( self, pth_gif=None ):
        if self._player:
            self._player.play( pth_gif )

    def shutdown( self ):
        if self._player:
            self._player.shutdown()