"""
    Generates edit tags UI.
"""
from index import account_mgmt, render_page

TOGGLE_HEAD = '''
    <script type="text/javascript">
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
	</script>'''


def get_edit_tags():
    """Returns edit tags page/index content."""
    return render_page(account_mgmt(), TOGGLE_HEAD)
