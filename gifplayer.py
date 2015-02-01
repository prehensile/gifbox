#!/usr/bin/env python

import pygame
import sys, os, subprocess, shutil
import tempfile
import re
import time
import threading

class GifSprite( pygame.sprite.Sprite ):
    
    def __init__(self, pos=(0, 0), frames=None, frame_dir=None, fit_rect=None ):
        super( GifSprite, self ).__init__()
        self._fit_rect = fit_rect
        self._current_frame = None
        self._glitch = False
        self.load( frame_dir=frame_dir, fit_rect=fit_rect )
        self.update()
    
    def load( self, frame_dir=None, fit_rect=None ):
        self._frame_source = FrameSource( frame_dir, fit_rect=fit_rect )

        fw, fh = self._fit_rect.width, self._fit_rect.height
        lw, lh = self._frame_source.logical_size
        if lw > lh:
            # landscape image
            self._scale_factor = float(fw)/float(lw)           
        else:
            # portrait image
            self._scale_factor = float(fh)/float(lh)

        self._logical_size = tuple([i*self._scale_factor for i in self._frame_source.logical_size])
        print "logical size frame: %s\nlogical size self:%s" % ( self._frame_source.logical_size, self._logical_size  )


    def update(self, *args):
        frame_next = self._frame_source.next_frame()
        if frame_next is not self._current_frame:
            self.image = pygame.image.load( frame_next.image_path ) 

            c = self._fit_rect.center

            pos = ( c[0] - (self._logical_size[0]/2),
                    c[1] - (self._logical_size[1]/2) )
            
            if not self._glitch:
                pos = ( pos[0] + (frame_next.offset[0] * self._scale_factor), 
                        pos[1] + (frame_next.offset[1] * self._scale_factor) ) 

            iw, ih = self.image.get_size()
            sz = ( int(iw*self._scale_factor), int(ih*self._scale_factor) )
            self.image = pygame.transform.scale( self.image, sz )

            self.rect = pygame.Rect( pos, self.image.get_size() )
        
            self._current_frame = frame_next

    def kill( self ):
        self._frame_source.destroy()
        super( GifSprite, self ).kill()


class Frame( object ):
    def __init__( self, index=0, delay=0, image_path=None, offset=(0,0) ):
        self.image_path = image_path
        self.delay = delay
        self.index = index
        self.offset = offset

class FrameSource( object ):

    def __init__( self, pth_gif=None, fit_rect=None ):
        self._fit_rect = fit_rect
        self.logical_size = (0,0)
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
       
        # parse logical size
        m = re.search( r'logical screen ([0-9]*)x([0-9]*)', buf )
        if m is not None:
            self.logical_size = ( int(m.group(1)), int(m.group(2)) )
            print self.logical_size

        # parse per-frame info
        blocks = buf.split("+")[1:]
        frames = []
        re_delay = re.compile( r'[\w\W]*delay ([0-9.]*)' )
        re_offset = re.compile( r'[\w\W]*at ([0-9,]*)' )
        idx = 0
        for block in blocks:
            d = 0
            offs = (0,0)
            m = re_delay.match(block)
            if m is not None:
                d = float( m.group(1) )
            m = re_offset.match(block)
            if m is not None:
                offs = m.group(1).split(",")
                offs = tuple([ int(i) for i in offs ])
            frame = Frame( idx, d, offset=offs )
            frames.append( frame )
            idx += 1
        return frames

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
        args = [ "gifsicle", "--explode", pth_gif, "--output", output ]
        print args
        subprocess.call( args )
        return temp_path


class GifPlayer( threading.Thread ):
    
    def __init__(self, arg):
        super(GifPlayer, self).__init__()
        self.arg = arg
        self.init_pygame()
    
    def init_pygame( self ):        
        pygame.init()
        self._screen = self.init_display( (640,480) )
        self_clock = None

    def init_display( self, sz=None ):
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

    def play( self, gif_path ):
        self._gif_path = gif_path
        self._stop = threading.Event()
        self.start()

    def run( self ):

        if not self._clock:
            self._clock = pygame.time.Clock()

        sr = self._screen.get_rect()
        gif_sprite = GifSprite( frame_dir=self._gif_path, fit_rect=sr )
        sprites = pygame.sprite.Group( gif_sprite )

        while not self._stop.isSet():
            event = pygame.event.poll()
            if (event is not None) and (event.type == pygame.QUIT):
                self._stop.set()
            self._clock.tick(60)
            sprites.update()
            sprites.draw( self._screen )
            pygame.display.flip()

        # exit main runloop
        gif_sprite.kill()

    def stop( self ):
        self._stop.set()

    def shutdown( self ):
        self.stop()
        pygame.display.quit()

if __name__ == '__main__':
    gifplayer = GifPlayer()
    gifplayer.init()

    gif_path = sys.argv[1]
    gifplayer.play( gif_path )

    try:
        while True:
            pass
    except:
        pass

    gifplayer.shutdown()
