import pygame
import sys, os, subprocess, shutil
import tempfile
import re
import time

class GifSprite( pygame.sprite.Sprite ):
    
    def __init__(self, pos=(0, 0), frames=None, frame_dir=None ):
        super( GifSprite, self ).__init__()
        self._frame_source = FrameSource( frame_dir )
        self.rect = pygame.Rect( pos, (0,0) )
        self._current_frame = None
        self.update()

    def update(self, *args):
        frame_next = self._frame_source.next_frame()
        if frame_next is not self._current_frame:
            self.image = pygame.image.load( frame_next.image_path ) 
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

    def __init__( self, pth_gif=None ):
        if pth_gif is not None:
            self.load( pth_gif )

    def load( self, pth_gif ):
        timings = self.parse_timings( pth_gif )
        frame_dir = self.extract_frames( pth_gif )
        frame_list = os.listdir( frame_dir )
        frame_list.sort()
        frames = []
        idx = 0
        for fn_gif in frame_list:
            fn_gif = os.path.join( frame_dir, fn_gif )
            frame = Frame( idx, timings[idx], fn_gif )
            frames.append( frame )
        self._frames = frames
        self._last_ts = time.time()
        self._current_frame = frames[0]
        self._idx_frame = 0

    def parse_timings( self, pth_gif ):
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
        timings = []
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
        args = [ "gifsicle", "--explode", pth_gif, "--output", output ]
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
    print gif_path

    clock = pygame.time.Clock()

    gif_sprite = GifSprite( frame_dir=gif_path )
    sprites = pygame.sprite.Group( gif_sprite )
    
    gif_sprite.rect.center = screen.get_rect().center 

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
