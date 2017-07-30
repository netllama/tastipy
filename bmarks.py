from bottle import route, request, get, post
from index import header0, do_bmarks, list_tags, footer


def get_bmarks():
    """Returns bmarks page/index content."""
    base_url = 'http://{se}{sc}/'.format(se=request.environ.get('SERVER_NAME'), sc=request.environ.get('SCRIPT_NAME'))
    return_data = ''
    top = '''<html lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>Tasti</title>
    <link rel="stylesheet" type="text/css" href="{h}css/main.css" />
</head>
<body><div id="wrapper">
        <div id="header">'''.format(h=base_url)
    return_data += top
    return_data += header0()
    return_data += '''</div>
    <div id="faux">
        <div id="leftcolumn">'''
    return_data += do_bmarks()
    return_data += '''<div class="clear"></div>
        </div>
        <div id="rightcolumn">
                '''
    return_data += list_tags()
    return_data += '''<div class="clear"></div>
        </div>
    </div>
    <div id="footer">'''
    return_data += footer()
    #return_data += str(request.environ)
    bottom = '''</div>
    </div>
</body>
</html>'''
    return_data += bottom
    return return_data
