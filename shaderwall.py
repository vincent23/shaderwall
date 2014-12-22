import bottle
import sqlite3 as sql
import base64
import random
import string
import json

app = application = bottle.Bottle()

bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024 # 1MB

@app.route('/')
@app.route('/gallery/<page:int>')
@bottle.view('static/gallery.html')
def get_gallery(page=1):
    items_per_page = 16
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM shader')
    total_shaders = cursor.fetchone()[0]
    total_pages = total_shaders / items_per_page + (1 if total_shaders % items_per_page != 0 else 0)
    cursor = conn.cursor()
    cursor.execute('SELECT id,source,created FROM shader ORDER by id DESC LIMIT ?, ?', (items_per_page * (page - 1), items_per_page))
    return { 'shaders': cursor.fetchall(), 'page': page, 'total_pages': total_pages }

@app.route('/edit')
@app.route('/edit/<shader_id:int>')
@bottle.view('static/editor.html')
def get_gallery(shader_id=None):
    if shader_id:
        authcode = bottle.request.params.getunicode('authcode')
        cursor = conn.cursor()
        cursor.execute('SELECT id, source, authcode FROM shader WHERE id = ?', (shader_id,))
        result = cursor.fetchone()
        if result:
            if result[2] == authcode:
                save_button_text = 'Save'
                save_url = '/shaders/%d' % shader_id
            else:
                save_button_text = 'Fork'
                save_url = '/shaders'
            return {
                'shader_id': result[0],
                'shader_source': result[1],
                'save_button_text': save_button_text,
                'save_url': save_url,
                'authcode': authcode,
            }
        else:
            return {'save_url': '/shaders', 'save_button_text': 'Create', 'authcode': ''}
    else:
        return {'save_url': '/shaders', 'save_button_text': 'Create', 'authcode': ''}

@app.route('/lib/<path:path>')
def get_static(path):
    return bottle.static_file(path, root='./static/lib')

@app.route('/screenshots/<path:path>')
def get_screenshot(path):
    return bottle.static_file(path, root='./uploads', mimetype='image/png')

# generate 32byte authentication code
def generate_authcode():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(32))

def save_screenshot(shader_id, screenshot):
    try:
        if not screenshot[:22] == 'data:image/png;base64,':
            return False
        screenshot = base64.b64decode(screenshot[22:])
        screenshot_file = open("uploads/%d.png" % shader_id, "w")
        screenshot_file.write(screenshot)
        screenshot_file.close()
        return True
    except:
        return False

@app.post('/shaders')
def create_shader():
    source = bottle.request.params.getunicode('source')
    screenshot = bottle.request.params.getunicode('screenshot')

    cursor = conn.cursor()
    new_authcode = generate_authcode()
    cursor.execute('INSERT INTO shader (source, authcode) VALUES (?,?)', (source,new_authcode))
    conn.commit()
    new_shader_id = cursor.lastrowid
    if not save_screenshot(new_shader_id, screenshot):
        cursor.execute('DELETE FROM shader WHERE id = ?', (new_shader_id))
        return bottle.abort(500, "Internal Server Error")

    return json.dumps({'id': new_shader_id, 'authcode': new_authcode, 'redirect': True})

@app.get('/shaders/<shader_id:int>')
def get_shader(shader_id):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM shader WHERE id = ?', (shader_id,))
    result = cursor.fetchone()
    if result:
        return str(result)
    else:
        bottle.abort(404, 'Shader not found')

@app.post('/shaders/<shader_id:int>')
def edit_shader(shader_id):
    source = bottle.request.params.getunicode('source')
    authcode = bottle.request.params.getunicode('authcode')
    screenshot = bottle.request.params.getunicode('screenshot')
    cursor = conn.cursor()
    cursor.execute('UPDATE shader SET source = ? WHERE id = ? AND authcode = ?' , (source, shader_id, authcode))
    conn.commit()
    if not save_screenshot(shader_id, screenshot):
        print("yo?")

    if cursor.rowcount == 1:
        return json.dumps({'id': shader_id, 'authcode': authcode, 'redirect': False})
    else:
        bottle.abort(403, 'Update failed')

def setup_db():
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS shader (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source TEXT,
                        authcode TEXT,
                        created TEXT DEFAULT CURRENT_TIMESTAMP
                      )''')
    conn.commit()

global conn
conn = sql.connect('shaderwall.db')
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
