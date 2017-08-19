from bottle import route, request, get, post
from index import header0, register, list_tags, footer


def do_register():
    """Returns registration page/index content."""
    base_url = 'http://{se}{sc}/'.format(se=request.environ.get('SERVER_NAME'),
                                         sc=request.environ.get('SCRIPT_NAME'))
    return_data = ''
    top = '''<html lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>Tasti</title>
    <link rel="stylesheet" type="text/css" href="{h}css/main.css" />
    <link rel="stylesheet" type="text/css" href="{h}css/jquery.validity.css" />

    <script type="text/javascript" src="{h}js/jquery.js"></script>
    <script type="text/javascript" src="{h}js/jquery.validity.js"></script>

    <script type="text/javascript">
            $(function() {{ 
                $("form").validity(function() {{
                $("#username")
                    .minLength(5, "Must be at least 5 characters") ;
                $("#password0")
                    .minLength(6, "Must be at least 6 characters") ;
                $("#password1")
    				.minLength(6, "Must be at least 6 characters") ;
                $("#email")
                    .match("email","Requires an email address")
                    .minLength(5, "Must be at least 5 characters");
                }});
            }});
    </script>
</head>
<body><div id="wrapper">
        <div id="header">'''.format(h=base_url)
    return_data += top
    return_data += header0(base_url)
    return_data += '''</div>
    <div id="faux">
        <div id="leftcolumn">'''
    return_data += register(base_url)
    return_data += '''<div class="clear"></div>
        </div>
        <div id="rightcolumn">
                '''
    return_data += list_tags(base_url)
    return_data += '''<div class="clear"></div>
        </div>
    </div>
    <div id="footer">'''
    return_data += footer(base_url)
    bottom = '''</div>
    </div>
</body>
</html>'''
    return_data += bottom
    return return_data
