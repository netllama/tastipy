"""
    Generates login UI.
"""
from index import header0, login, list_tags, footer


def do_login():
    """Returns login page/index content."""
    return_data = ''
    top = '''<html lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>Tasti</title>
    <link rel="stylesheet" type="text/css" href="main.css" />
</head>
<body><div id="wrapper">
        <div id="header">'''
    return_data += top
    return_data += header0()
    return_data += '''</div>
    <div id="faux">
        <div id="leftcolumn">'''
    return_data += login()
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
    bottom = '''</div>
    </div>
</body>
</html>'''
    return_data += bottom
    return return_data
