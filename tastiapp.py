from bottle import route, template, error, request, static_file, get, post
from index import get_index
from bmarks import get_bmarks
from tags import get_tags
from add import add_tags
from bmarklet import get_bmarklet
from account import get_account
from edit_tags import get_edit_tags
from importbm import get_import_bm
from edit import do_edit
from login import do_login
from register import do_register

@route('/')
def myroot():
    return_data = get_index()
    return return_data

@route('/account', method=['GET', 'POST'])
def bmarks():
    return_data = get_bmarklet()
    return return_data

@route('/add', method=['GET', 'POST'])
def bmarks():
    return_data = add_tags()
    return return_data

@route('/bmarklet')
def bmarks():
    return_data = get_bmarklet()
    return return_data

@route('/bmarks')
def bmarks():
    return_data = get_bmarks()
    return return_data

@route('/edit', method=['GET', 'POST'])
def bmarks():
    return_data = do_edit()
    return return_data

@route('/edit_tags', method=['GET', 'POST'])
def bmarks():
    return_data = get_edit_tags()
    return return_data

@route('/import', method=['GET', 'POST'])
def bmarks():
    return_data = get_import_bm()
    return return_data

@route('/login', method=['GET', 'POST'])
def bmarks():
    return_data = do_login()
    return return_data

@route('/register', method=['GET', 'POST'])
def bmarks():
    return_data = do_register()
    return return_data

@route('/tags')
def bmarks():
    return_data = get_tags()
    return return_data

# serve css
@get('/<filename:re:.*\.css>')
def send_css(filename):
    return static_file(filename, root='css')

# serve javascript
@get('/<filename:re:.*\.js>')
def send_js(filename):
    return static_file(filename, root='js')

# serve images
@get('<filename:re:.*\.png>')
def send_img(filename):
    return static_file(filename, root='images')

# serve fonts
@get('<filename:re:.*\.(woff|woff2)>')
def send_font(filename):
    return static_file(filename, root='fonts')

@error(404)
def handle404(error):
    return '<H1>Ooops, its not here<BR>'

@error(500)
def handle500(error):
    return '<H1>Oops, its broken:&nbsp;{}<BR>'.format(error)
