from bottle import route, template, error, request, static_file, get, post
from index import get_index
from bmarks import get_bmarks
#account, add, bmarklet, bmarks, edit, edit_tags, importbm, login, tags

@route('/')
def myroot():
	return_data = get_index()
	return return_data

@route('/account')
def bmarks():
	return 'account'

@route('/add')
def bmarks():
	return 'add'

@route('/bmarklet')
def bmarks():
	return 'bmarklet'

@route('/bmarks')
def bmarks():
	return_data = get_bmarks()
	return return_data

@route('/edit')
def bmarks():
	return 'edit'

@route('/edit_tags')
def bmarks():
	return 'edit_tags'

@route('/import')
def bmarks():
	return 'import'

@route('/login')
def bmarks():
	return 'login'

@route('/tags')
def bmarks():
	return 'tags'
	
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
