"""
    Generates bookmark edit UI.
"""
from index import edit_bmarks, render_page, FORM_VALIDATION_HEAD


def do_edit():
    """Returns edit page/index content."""
    return render_page(edit_bmarks(), FORM_VALIDATION_HEAD)
