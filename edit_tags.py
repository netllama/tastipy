from bottle import route, request, get, post
from index import header0, account_mgmt, list_tags, footer


def get_edit_tags():
    """Returns edit tags page/index content."""
    base_url = 'http://{se}{sc}/'.format(se=request.environ.get('SERVER_NAME'),
                                         sc=request.environ.get('SCRIPT_NAME'))
    return_data = ''
    top = '''<html lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>Tasti</title>
    <link rel="stylesheet" type="text/css" href="{h}css/main.css" />'''.format(h=base_url)

    top += '''<script type="text/javascript">
		function toggle(aId) {
			var collection = document.getElementById(aId).getElementsByTagName("input");
			for (var x=0; x<collection.length; x++) {
				if (collection[x].type.toLowerCase() == "checkbox") {
					if (collection[x].checked) {
						collection[x].checked = false;
					}
					else {collection[x].checked = true}
				}
			}
		}
	</script>
</head>
<body><div id="wrapper"><div id="header">'''

    return_data += top
    return_data += header0(base_url)
    return_data += '''</div>
    <div id="faux">
        <div id="leftcolumn">'''
    return_data += account_mgmt(base_url)
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
