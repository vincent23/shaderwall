import bottle
import base64
import json
import time
import datetime
from database import Shader, Vote, setup_db, db_session
from sqlalchemy.sql import exists
from PIL import Image

screenshot_size = (400, 300)

app = application = bottle.Bottle()
bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024 # 1MB

default_shader_source_file = open("default.shader", "r")
default_shader_source = default_shader_source_file.read()
default_shader_source_file.close()

@app.route('/')
@app.route('/gallery/<page:int>')
@bottle.view('static/gallery.html')
def get_gallery(page=1):
    session = db_session()
    items_per_page = 16
    shaders = session.query(Shader)
    total_pages = shaders.count() / items_per_page + (1 if shaders.count() % items_per_page != 0 else 0)
    session.close()

    return { 'shaders': shaders.order_by(Shader.updated.desc()).offset(items_per_page * (page - 1)).limit(items_per_page).all(), 'page': page, 'total_pages': total_pages }

@app.route('/wall/wat')
def wat_wall():
    datfile = open("watid","r")
    datid = int(datfile.read())
    datfile.close()
    return json.dumps({'id': datid})

@app.route('/wall')
@app.route('/wall/<shader_id:int>')
@bottle.view('static/wall.html')
def get_wall(shader_id=None):
    if shader_id:
        try:
            session = db_session()
            shader = session.query(Shader).filter(Shader.id == shader_id).one()
            session.close()
            return {
                'shader_id': shader.id,
                'shader_source': shader.source,
                'save_button_text': '',
                'save_url': '',
                'authcode': '',
            }
        except:
            return {'save_url': '', 'save_button_text': '', 'authcode': '', 'screenshot_size': screenshot_size}
    else:
        return {'save_url': '', 'save_button_text': '', 'authcode': '', 'screenshot_size': screenshot_size}

@app.route('/edit')
@app.route('/edit/<shader_id:int>')
@app.route('/<shader_id:int>')
@bottle.view('static/editor.html')
def get_gallery(shader_id=None):
    if shader_id:
        authcode = bottle.request.params.getunicode('authcode')
        try:
            session = db_session()
            shader = session.query(Shader).filter(Shader.id == shader_id).one()

            votes = session.query(Vote).filter(Vote.shader_id == shader_id, Vote.ip == bottle.request.environ.get('REMOTE_ADDR'))
            if votes.count() > 0:
                voting_disabled = ' disabled'
                vote = 'up' if votes.one().value > 0 else 'down'
            else:
                voting_disabled = ''
                vote = None

            shader.views += 1
            session.commit()
            if shader.authcode == authcode:
                save_button_text = 'Save'
                save_url = '/shaders/%d' % shader_id
            else:
                save_button_text = 'Fork'
                save_url = '/shaders'
            session.close()
            return {
                'shader_id': shader.id,
                'shader_source': shader.source,
                'save_button_text': save_button_text,
                'save_url': save_url,
                'authcode': authcode,
                'screenshot_size': screenshot_size,
                'voting_disabled': voting_disabled,
                'vote': vote
            }
        except:
            return {'save_url': '/shaders', 'save_button_text': 'Create', 'authcode': '', 'screenshot_size': screenshot_size, 'shader_source': default_shader_source, 'voting_disabled': '', 'vote': None }
    else:
        return {'save_url': '/shaders', 'save_button_text': 'Create', 'authcode': '', 'screenshot_size': screenshot_size, 'shader_source': default_shader_source, 'voting_disabled': '', 'vote': None }

@app.route('/help')
@bottle.view('static/help.html')
def get_help():
    return {}

@app.route('/lib/<path:path>')
def get_static(path):
    return bottle.static_file(path, root='./static/lib')

@app.route('/screenshots/<path:path>')
def get_screenshot(path):
    return bottle.static_file(path, root='./uploads', mimetype='image/png')

def save_screenshot(shader_id, screenshot):
    try:
        if not screenshot[:22] == 'data:image/png;base64,':
            return False
        screenshot = base64.b64decode(screenshot[22:])
        screenshot_file = open("uploads/%d.png" % shader_id, "w")
        screenshot_file.write(screenshot)
        screenshot_file.close()
        im = Image.open("uploads/%d.png" % shader_id)
        if im.size != screenshot_size:
            raise('Eh, wrong screenshot size...')
        return True
    except:
        try:
            dummy_file = open("static/broken.png", "r")
            screenshot_file = open("uploads/%d.png" % shader_id, "w")
            screenshot_file.write(dummy_file.read())
            screenshot_file.close()
        except:
            pass
        return False

def unixtime():
    return int(time.time())

@app.post('/shaders')
def create_shader():
    source = bottle.request.params.getunicode('source')
    screenshot = bottle.request.params.getunicode('screenshot')

    session = db_session()
    shader = Shader(source=source)
    session.add(shader)
    session.commit()
    if not save_screenshot(shader.id, screenshot):
        shader.delete()
        session.commit()
        session.close()
        return bottle.abort(500, "Internal Server Error")

    session.close()
    return json.dumps({'id': shader.id, 'authcode': shader.authcode, 'redirect': True})

@app.post('/shaders/<shader_id:int>')
def edit_shader(shader_id):
    source = bottle.request.params.getunicode('source')
    authcode = bottle.request.params.getunicode('authcode')
    screenshot = bottle.request.params.getunicode('screenshot')
    session = db_session()
    try:
        shader = session.query(Shader).filter(Shader.id == shader_id)
        if shader.count():
            shader = shader.one()
        else:
            session.close()
            raise('Shader not found')
        if not shader.authcode == authcode:
            session.close()
            return bottle.abort(403, 'Forbidden')
    except:
        session.close()
        return bottle.abort(404, 'Not found')

    try:
        shader.source = source
        shader.updated = datetime.datetime.now()
        session.commit()
        session.close()
    except:
        return bottle.abort(500, 'Internal Server Error')

    if not save_screenshot(shader_id, screenshot):
        print("yo?")

    return json.dumps({'id': shader_id, 'authcode': authcode, 'redirect': False})

@app.post('/vote')
def vote():
    shader_id = bottle.request.params.getunicode('id')
    vote = bottle.request.params.getunicode('vote')
    ip = bottle.request.environ.get('REMOTE_ADDR')
    voting_dict = {
        'up': 1,
        'piggy': 0,
        'down': -1
    }

    session = db_session()
    if not session.query(exists().where(Shader.id==shader_id)):
        return bottle.abort(404, 'Not Found')

    voting = Vote(
        shader_id = shader_id,
        ip = ip,
        value = voting_dict[vote]
    )

    existing_vote = session.query(Vote).filter(Vote.shader_id == shader_id, Vote.ip == ip)
    if existing_vote.count():
        session.close()
        return bottle.abort(403, 'Forbidden')

    try:
        session.add(voting)
        session.commit()
        session.close()
    except:
        return bottle.abort(500, 'Internal Server Error')

    return json.dumps({'error': 'success'})

setup_db()

class StripPathMiddleware(object):
    '''
    Get that slash out of the request
    '''
    def __init__(self, a):
        self.a = a
    def __call__(self, e, h):
        e['PATH_INFO'] = e['PATH_INFO'].rstrip('/')
        return self.a(e, h)

if __name__ == '__main__':
    bottle.run(app=StripPathMiddleware(app), host='localhost', port=8080, debug=True)
