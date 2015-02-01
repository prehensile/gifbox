# -*- coding: utf-8 -*-

import os, sys
import cherrypy
import jinja2
from dropbox.client import DropboxClient, DropboxOAuth2Flow
from morris import signal

@signal
def token_saved( pth_token ):
    pass

class InterfaceViews( object ):

    def __init__( self, pth_token ):
        self._dropbox_app_key = os.environ.get( "DROPBOX_KEY" )
        self._dropbox_app_secret = os.environ.get( "DROPBOX_SECRET" )
        self._jinja_env = jinja2.Environment( 
            loader=jinja2.FileSystemLoader('public')
        )
        self._pth_token = pth_token

    def save_token( self, token ):
        pth_dir = os.path.dirname( self._pth_token )
        if not os.path.exists( pth_dir ):
            os.makedirs( pth_dir )
        fh = open( self._pth_token, "w" )
        fh.write( token )
        fh.close()
        token_saved( self._pth_token )

    def render_template( self, template, **kwargs ):
        tmpl = self._jinja_env.get_template( template )
        return tmpl.render( **kwargs )

    @cherrypy.expose
    def login( self, username=None ):
        error = None
        if username:
            cherrypy.session['user'] = username
            # flash('You were logged in')
            #return redirect( cherrypy.url('home'))
            raise cherrypy.HTTPRedirect( cherrypy.url("home") )
        else:
            error = "You must provide a username"
        return self.render_template('login.html', error=error)

    @cherrypy.expose
    def home( self ):
        user = None
        try:
            user = cherrypy.session['user']
        except:
            pass

        if not user:
            raise cherrypy.HTTPRedirect( cherrypy.url('login') )
        access_token = cherrypy.session.get("access_token")
        real_name = None
        if access_token is not None:
            client = DropboxClient( access_token )
            account_info = client.account_info()
            real_name = account_info["display_name"]
        return self.render_template( 'index.html', real_name=real_name, user=user )

    @cherrypy.expose
    def dropbox_auth_finish( self, state=None, code=None ):
        username = cherrypy.session.get('user')
        if username is None:
            raise cherrypy.HTTPError( 403 )
        try:
            access_token, user_id, url_state = self.get_auth_flow().finish( cherrypy.request.params )
        except DropboxOAuth2Flow.BadRequestException:
            raise cherrypy.HTTPError( 400 )
        except DropboxOAuth2Flow.BadStateException:
            raise cherrypy.HTTPError( 400 )
        except DropboxOAuth2Flow.CsrfException:
            raise cherrypy.HTTPError( 403 )
        except DropboxOAuth2Flow.NotApprovedException:
            cherrypy.log( "Not approved", traceback=True )
            error = 'Not approved?  Why not'
            raise cherrypy.HTTPRedirect( cherrypy.url('home'), error=error )
        except:
            cherrypy.log( "Auth error", traceback=True )
            raise cherrypy.HTTPError( 403 )
        #data = [access_token, username]
        # TODO: save token
        self.save_token( access_token )
        raise cherrypy.HTTPRedirect( cherrypy.url('home') )

    @cherrypy.expose
    def dropbox_auth_start( self ):
        if 'user' not in cherrypy.session:
            raise cherrypy.HTTPError( 403 )
        raise cherrypy.HTTPRedirect(  self.get_auth_flow().start() )
    

    def get_auth_flow( self ):
        redirect_uri =  cherrypy.url( 'dropbox_auth_finish' )
        return DropboxOAuth2Flow( self._dropbox_app_key, self._dropbox_app_secret, redirect_uri,
                                           cherrypy.session, 'dropbox-auth-csrf-token' )

class WebInterface( object ):
    
    def __init__( self, pth_token ):
        self._pth_token = pth_token
        
    def start( self ):
        pth_root = os.path.abspath( os.getcwd() )
        conf = {
             '/': {
                 'tools.sessions.on': True,
                 'tools.staticdir.root': pth_root
             },
              '/static': {
                 'tools.staticdir.on': True,
                 'tools.staticdir.dir': os.path.join( pth_root, 'public' )
             }
        }
        
        cherrypy.engine.signal_handler.subscribe()
        cherrypy.config.update( conf )
        
        views = InterfaceViews( self._pth_token )
        cherrypy.tree.mount( views, "", config=conf )
        cherrypy.engine.start()

    def shutdown( self ):
        cherrypy.engine.exit()

if __name__ == '__main__':
    pth_token = sys.argv[1]
    print pth_token
    interface = WebInterface( pth_token )
    interface.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        pass

    interface.stop()
