"""
Generates get_tags UI.
"""
from index import do_tags, render_page


def get_tags():
    """Returns tags page/index content."""
    return render_page(do_tags())
