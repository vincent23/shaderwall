import bottle
import sqlite3 as sql
import base64

bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024 # 1MB

def main():
    global conn
    conn = sql.connect('shaderwall.db')
    setup_db()
    bottle.run(host='localhost', port=8080, debug=True)

@bottle.route('/')
@bottle.view('static/gallery.html')
def get_gallery():
    cursor = conn.cursor()
    cursor.execute('SELECT id,source,created FROM shader')
    return { 'shaders': cursor.fetchall() }

@bottle.route('/edit')
@bottle.route('/edit/<shader_id:int>')
@bottle.view('static/editor.html')
def get_gallery(shader_id=None):
    if shader_id:
        cursor = conn.cursor()
        cursor.execute('SELECT id, source FROM shader WHERE id = ?', (shader_id,))
        result = cursor.fetchone()
        if result:
            return {
                'shader_id': result[0],
                'shader_source': result[1],
            }
        else:
            return {}
    else:
        return {}

@bottle.route('/lib/<path:path>')
def get_static(path):
    return bottle.static_file(path, root='./static/lib')

@bottle.route('/screenshots/<path:path>')
def get_screenshot(path):
    return bottle.static_file(path, root='./uploads')

@bottle.post('/shaders')
def create_shader():
    source = bottle.request.params.getunicode('source')
    screenshot = bottle.request.params.getunicode('screenshot')
    if not screenshot[:22] == 'data:image/png;base64,':
        return bottle.abort(418, "I'm a teapot.")

    cursor = conn.cursor()
    cursor.execute('INSERT INTO shader (source) VALUES (?)', (source,))
    conn.commit()
    new_shader_id = cursor.lastrowid
    try:
        screenshot = base64.b64decode(screenshot[22:])
        open("uploads/%d.png" % cursor.lastrowid, "w").write(screenshot);
    except:
        cursor.execute('DELETE FROM shader WHERE id = ?', (new_shader_id))
        return bottle.abort(500, "Internal Server Error")

    return 'Created new shader ' + str(cursor.lastrowid)

@bottle.get('/shaders/<shader_id:int>')
def get_shader(shader_id):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM shader WHERE id = ?', (shader_id,))
    result = cursor.fetchone()
    if result:
        return str(result)
    else:
        bottle.abort(404, 'Shader not found')

@bottle.post('/shaders/<shader_id:int>')
def edit_shader(shader_id):
    source = bottle.request.params.getunicode('source')
    authcode = bottle.request.params.getunicode('authcode')
    cursor = conn.cursor()
    cursor.execute('UPDATE shader SET source = ? WHERE id = ? AND authcode = ?' , (source, shader_id, authcode))
    conn.commit()
    if cursor.rowcount == 1:
        return 'Updated shader'
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

main()
