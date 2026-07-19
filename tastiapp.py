"""
    Top level app routing definitions.
"""
from bottle import route, error, static_file, get
from index import get_index
from bmarks import get_bmarks
from tags import get_tags
from add import add_tags
from bmarklet import get_bmarklet
from edit_tags import get_edit_tags
from importbm import get_import_bm
from edit import do_edit
from login import do_login
from register import do_register


@route('/')
def myroot():
    """Serve the top level index page."""
    return get_index()


@route('/account', method=['GET', 'POST'])
def account_route():
    """Serve the account page."""
    return get_bmarklet()


@route('/add', method=['GET', 'POST'])
def add_route():
    """Serve the add bookmark page."""
    return add_tags()


@route('/bmarklet')
def bmarklet_route():
    """Serve the bookmarklet page."""
    return get_bmarklet()


@route('/bmarks')
def bmarks_route():
    """Serve the bookmarks page."""
    return get_bmarks()


@route('/edit', method=['GET', 'POST'])
def edit_route():
    """Serve the bookmark edit page."""
    return do_edit()


@route('/edit_tags', method=['GET', 'POST'])
def edit_tags_route():
    """Serve the edit tags page."""
    return get_edit_tags()


@route('/import', method=['GET', 'POST'])
def import_route():
    """Serve the bookmark import page."""
    return get_import_bm()


@route('/login', method=['GET', 'POST'])
def login_route():
    """Serve the login page."""
    return do_login()


@route('/register', method=['GET', 'POST'])
def register_route():
    """Serve the registration page."""
    return do_register()


@route('/tags')
def tags_route():
    """Serve the tags page."""
    return get_tags()


# serve css
@get(r'/<filename:re:.*\.css>')
def send_css(filename):
    """Serve CSS static files."""
    return static_file(filename, root='css')


# serve javascript
@get(r'/<filename:re:.*\.js>')
def send_js(filename):
    """Serve JavaScript static files."""
    return static_file(filename, root='js')


# serve images
@get(r'<filename:re:.*\.png>')
def send_img(filename):
    """Serve PNG image static files."""
    return static_file(filename, root='images')


# serve fonts
@get(r'<filename:re:.*\.(woff|woff2)>')
def send_font(filename):
    """Serve font static files."""
    return static_file(filename, root='fonts')


@error(404)
def handle404():
    """Render the 404 error page."""
    return '<H1>Ooops, its not here<BR>'


@error(500)
def handle500(err):
    """Render the 500 error page."""
    return f'<H1>Oops, its broken:&nbsp;{err}<BR>'
