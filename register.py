"""
    Generates registration UI.
"""
from index import register, render_page, JQUERY_VALIDITY_HEAD

REGISTER_HEAD = JQUERY_VALIDITY_HEAD + '''
                $("#username")
                    .minLength(5, "Must be at least 5 characters") ;
                $("#password0")
                    .minLength(6, "Must be at least 6 characters") ;
                $("#password1")
                    .minLength(6, "Must be at least 6 characters") ;
                $("#email")
                    .match("email","Requires an email address")
                    .minLength(5, "Must be at least 5 characters");
                }});
            }});
    </script>'''


def do_register():
    """Returns registration page/index content."""
    return render_page(register(), REGISTER_HEAD)
