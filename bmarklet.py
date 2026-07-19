"""
    Generates bookmarklet page content.
"""
from index import account_mgmt, render_page


def get_bmarklet():
    """Returns bookmarklet page/index content."""
    return render_page(account_mgmt())
