import subprocess 

class GifPlayerOSX( object ):
    
    def __init__( self ):
        self._process = None

    def stop( self ):
        if self._process:
            self._process.kill()
            self._process = None

    def play( self, pth_gif ):
        self.stop()
        args = [ "qlmanage", "-p", pth_gif ]
        self._process = subprocess.Popen( args )    

    def shutdown( self ):
        self.stop()

