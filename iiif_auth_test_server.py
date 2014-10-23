#!/usr/bin/env python
"""Test code for IIIF Authentication

Based on work at 2014-10-20/21/22/23 London IIIF 6 meeting, see:
<https://github.com/IIIF/iiif.io/blob/master/source/event/2014/london_notes.md>
<https://github.com/IIIF/iiif.io/blob/master/source/event/2014/london_auth_scenarios.md>

Contains code copied from
<https://github.com/pulibrary/arkify_web/blob/development/arkform/app.py>
<http://flask.pocoo.org/docs/0.10/api/#application-globals>
"""
from flask import Flask, Response, request, redirect, make_response, render_template_string, send_from_directory, abort
import os
import sys

try:
    app = Flask(__name__)
    #config = configure()
    #init_db(config['db']['path'])
    #app.secret_key = config['cas']['secret']
    #session_lifetime = timedelta(seconds=config['cas']['session_age'])
    #app.permanent_session_lifetime = session_lifetime
except Exception as e:
    sys.stderr.write(str(e)+'\n')
    exit(1)

MENU = '''
<p>[ <a href="/">home</a> | 
<a href="/img/image.png">public image</a> | <a href="/page_with_img">public page with public and auth images</a> |  
<a href="/auth/page.html">auth_page</a> | <a href="/auth/image.png">auth_image</a> | 
<a href="/cookie_auth">cookie_auth</a> | <a href="/cookie_unauth">cookie_unauth</a> ]</p>
'''

def html_content(html):
    """Wrap html string with HTML header (menu and current debugging info) and footer
    """
    cookies = str(request.cookies)
    return render_template_string(MENU+"<p>Cookies: "+cookies+"</p><div>"+html+"</div>")

@app.route('/')
def index():
    return html_content('<p>Homepage (public)</p>')

@app.route('/page_with_img')
def page_with_img():
    return html_content('<p>Here is an image: <img src="/img/image.png" alt="unauth image"/></p><p>and here is another with auth: <img src="/auth/image.png" alt="auth image"/></p>')

def has_cookie_auth():
    sys.stderr.write(request.cookies.get('auth_cookie','NUTTIN')+'\n')
    return (request.cookies.get('auth_cookie','') == 'very_secret_cookie' )

@app.route('/img/<string:file>')
def image(file):
    """Any file in img directory, no auth required"""
    dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),'img')
    return send_from_directory(dir,file)

@app.route('/auth/page.html')
def auth_page():
    if (has_cookie_auth()):
        return html_content('A page that requires cookie auth: authorized')
    else:
        abort(401)
         
@app.route('/auth/image.png')
def auth_image():
	if (has_cookie_auth()):
		return image('image.png')
	else:
		abort(401)

@app.route('/cookie_auth')
def cookie_auth():
	resp = make_response(html_content("setting auth_cookie"))
	resp.set_cookie('auth_cookie', 'very_secret_cookie')
	return resp

@app.route('/cookie_unauth')
def cookie_unauth():
	resp = make_response(html_content("clearing auth_cookie"))
	resp.set_cookie('auth_cookie', '', expires=0)
	return resp

@app.errorhandler(401)
def code401(error):
    return Response('<p>401: You must go to <a href="/cookie_auth">cookie_auth</a> to authenticate</p>',401,{'WWWAuthenticate':'Basic realm="Login Required"'})

if __name__ == '__main__':
    app.run(debug=True)