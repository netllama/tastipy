from bottle import route, template, error, request, static_file, get, post
from index import get_index
from bmarks import get_bmarks
from tags import get_tags
from add import add_tags
from bmarklet import get_bmarklet
from account import get_account
from edit_tags import get_edit_tags
#account, add, edit, importbm, login

@route('/')
def myroot():
    return_data = get_index()
    return return_data

@route('/account')
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

@route('/edit')
def bmarks():
    return 'edit'

@route('/edit_tags', method=['GET', 'POST'])
def bmarks():
    return_data = get_edit_tags()
    return return_data

@route('/import')
def bmarks():
    return 'import'

@route('/login')
def bmarks():
    return 'login'

@route('/register')
def bmarks():
    return 'register'

@route('/tags')
def bmarks():
    return_data = get_tags()
    return return_data
	
# serve css
@route('/css/<filename:path>')
def send_css(filename):
    return static_file(filename, root='/var/www/tasti/css')

# serve javascript
@route('/js/<filename:re:.*\.js>')
def send_js(filename):
    return static_file(filename, root='/var/www/tasti/js')

# serve images
@route('/images/<filename:re:.*\.png>')
def send_img(filename):
    return static_file(filename, root='/var/www/tasti/images')

@route('/hello')
def hello():
    return '<H2>Hello World!<BR><BR><A HREF="https://google.com">Up</a>'

@route('/hello/<name>')
def idx(name='Stranger'):
    return template('<b>Hello {{name}}</b>!', name=name)

@error(404)
def handle404(error):
    return '<H1>Ooops, its not here<BR>'

@error(500)
def handle500(error):
    return '<H1>Oops, its broken:&nbsp;{}<BR>'.format(error)
