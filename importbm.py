"""
    Generates bookmark import UI.
"""
from index import account_mgmt, render_page


def get_import_bm():
    """Returns bmarks import content."""
    return render_page(account_mgmt())
