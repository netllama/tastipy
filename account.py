"""
    Generates account info UI.
"""
from index import account_mgmt, render_page


def get_account():
    """Returns account page/index content."""
    return render_page(account_mgmt())
