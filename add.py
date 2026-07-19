"""
    Generates add tags UI.
"""
from index import do_add, render_page, FORM_VALIDATION_HEAD


def add_tags():
    """Returns add bmarks page/index content."""
    return render_page(do_add(), FORM_VALIDATION_HEAD)
