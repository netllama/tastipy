from bottle import route, request, get, post
from index import header0, account_mgmt, list_tags, footer


def get_edit_tags():
    """Returns edit tags page/index content."""
    return_data = ''
    top = '''<html lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>Tasti</title>
    <link rel="stylesheet" type="text/css" href="main.css" />'''

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
    return_data += header0()
    return_data += '''</div>
    <div id="faux">
        <div id="leftcolumn">'''
    return_data += account_mgmt()
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
