import pygame
import sys, os, subprocess, shutil
import tempfile
import re
import time

class GifSprite( pygame.sprite.Sprite ):
    
    def __init__(self, pos=(0, 0), rect=None, frames=None, frame_dir=None ):
        super( GifSprite, self ).__init__()
        self._frame_source = FrameSource( frame_dir, fit_rect=rect )
        self.rect = rect
        self._fit_rect = rect
        self._current_frame = None
        self.update()

    def update(self, *args):
        frame_next = self._frame_source.next_frame()
        if frame_next is not self._current_frame:
            self.image = pygame.image.load( frame_next.image_path ) 
            
            fw, fh = self._fit_rect.width, self._fit_rect.height
            iw, ih = self.image.get_width(), self.image.get_height()
            if iw > ih:
                # landscape image
                fh = (ih/iw) * fw
            else:
                # portrait image
                fw = (iw/ih * fh)
            self.image = pygame.transform.scale( self.image, (fw,fh) )

            c = self.rect.center
            self.rect.width, self.rect.height = self.image.get_size()
            self.rect.center = c
            self._current_frame = frame_next

    def kill( self ):
        self._frame_source.destroy()
        super( GifSprite, self ).kill()


class Frame( object ):
    def __init__( self, index, delay, image_path ):
        self.image_path = image_path
        self.delay = delay
        self.index = index

class FrameSource( object ):

    def __init__( self, pth_gif=None, fit_rect=None ):
        self._fit_rect = fit_rect
        if pth_gif is not None:
            self.load( pth_gif )

    def load( self, pth_gif ):
        # get a list of frames from disk, make sure they're in order
        self._frame_dir = self.extract_frames( pth_gif )
        frame_list = os.listdir( self._frame_dir )
        frame_list.sort()
        # parse frame info, get a list of Frame objects
        frames = self.parse_info( pth_gif )
        # insert frame filenames into Frame list
        idx = 0
        for fn_gif in frame_list:
            frame = frames[idx]
            frame.image_path = os.path.join( self._frame_dir, fn_gif )
            idx +=1 
        self._frames = frames
        self._last_ts = time.time()
        self._current_frame = frames[0]
        self._idx_frame = 0

    def parse_info( self, pth_gif ):
        ''' 
        Use gifsicle to extract frame timings from a gif 
        Args: 
            pth_gif (str): the path to a gif file
        Returns:
            a list of frame timings, in seconds 
        '''
        args = [ "gifsicle", "--info", pth_gif ]
        buf = subprocess.check_output( args )
        blocks = buf.split("+")[1:]
        frames = []
        re_delay = re.compile( r'[\w\W]*delay ([0-9.]*)' )
        for block in blocks:
            m = re_delay.match(block)
            if m is not None:
                timings.append( float( m.group(1) ))
        return timings

    def next_frame( self ):
        ts = time.time()
        elapsed = ts - self._last_ts
        if elapsed > self._current_frame.delay:
            idx_frame = self._idx_frame + 1
            if idx_frame >= len( self._frames ):
                idx_frame = 0
            self._current_frame = self._frames[ idx_frame ]
            self._idx_frame = idx_frame
            self._last_ts = ts
        return self._current_frame 

    def destroy( self ):
        shutil.rmtree( self._frame_dir )

    def extract_frames( self, pth_gif ):
        gif_name = os.path.basename( pth_gif )
        temp_path = tempfile.mkdtemp()
        output = os.path.join( temp_path, gif_name )
        sz = "%dx%d" % ( self._fit_rect.width, self._fit_rect.height )
        args = [ "gifsicle", "--resize-fit", sz, "--explode", pth_gif, "--output", output ]
        print args
        subprocess.call( args )
        return temp_path

def init_display( sz=None ):
    # Start with fbcon since directfb hangs with composite output
    drivers = ['fbcon', 'directfb', 'svgalib']
    found = False
    for driver in drivers:
        # Make sure that SDL_VIDEODRIVER is set
        if not os.getenv('SDL_VIDEODRIVER'):
            os.putenv('SDL_VIDEODRIVER', driver)
            try:
                pygame.display.init()
            except pygame.error:
                print 'Driver: {0} failed.'.format(driver)
                continue
            found = True
            break

    if not found:
        raise Exception('No suitable video driver found!')
    
    flags = 0
    if found:
        d = pygame.display.Info()
        #flags = pygame.HWSURFACE | pygame.FULLSCREEN | pygame.DOUBLEBUF
        #sz = (d.current_w, d.current_h)
    else:
        pygame.display.init()
    screen = pygame.display.set_mode( sz, flags )
    return screen

def main():
    pygame.init()
    screen = None
    screen = init_display( (640,480) )

    gif_path = sys.argv[1]

    clock = pygame.time.Clock()

    sr = screen.get_rect()
    gif_sprite = GifSprite( frame_dir=gif_path, rect=sr)
    sprites = pygame.sprite.Group( gif_sprite )
    

    while True:
        event = pygame.event.poll()
        if (event is not None) and (event.type == pygame.QUIT):
            gif_sprite.kill()
            pygame.display.quit()
            sys.exit() 
        
        clock.tick(60)
        sprites.update()
        sprites.draw( screen )
        pygame.display.flip()

if __name__ == '__main__':
    main()
