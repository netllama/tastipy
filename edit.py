"""
    Generates bookmark edit UI.
"""
from index import header0, list_tags, footer, edit_bmarks


def do_edit():
    """Returns edit page/index content."""
    return_data = ''
    top = '''<html lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>Tasti</title>
    <link rel="stylesheet" type="text/css" href="main.css" />
    <link rel="stylesheet" type="text/css" href="jquery.validity.css" />

    <script type="text/javascript" src="jquery.js"></script>
	<script type="text/javascript" src="jquery.validity.js"></script>
	
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
        <div id="header">'''
    return_data += top
    return_data += header0()
    return_data += '''</div>
    <div id="faux">
        <div id="leftcolumn">'''
    return_data += edit_bmarks()
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
