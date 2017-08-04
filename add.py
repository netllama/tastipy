from bottle import route, request, get, post
from index import header0, do_add, list_tags, footer


def add_tags():
    """Returns bmarks page/index content."""
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
				$("#name")
    					.minLength(2, "Must be at least 2 characters") ;
				$("#url")
    					.match("url","Requires a valid URL (http://...)")
					.minLength(6, "Must be at least 6 characters");				
        		}});
    		}});
	</script>
</head>
<body><div id="wrapper">
        <div id="header">'''.format(h=base_url)
    return_data += top
    return_data += header0()
    return_data += '''</div>
    <div id="faux">
        <div id="leftcolumn">'''
    return_data += do_add()
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
