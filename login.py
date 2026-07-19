"""
    Generates login UI.
"""
from index import login, render_page


def do_login():
    """Returns login page/index content."""
    return render_page(login())
