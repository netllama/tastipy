"""
    Generates boomarks page UI.
"""
from index import do_bmarks, render_page


def get_bmarks():
    """Returns bmarks page/index content."""
    return render_page(do_bmarks())
