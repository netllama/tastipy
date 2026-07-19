"""
    Generates toplevel index.
"""
from os import chdir, path

# Change working directory so relative paths (and template lookup) work again
chdir(path.dirname(__file__))

import bottle  # pylint: disable=wrong-import-position
# tastiapp is imported for its side effects: importing it registers all of the
# application's routes on bottle's default app.
import tastiapp  # pylint: disable=wrong-import-position,unused-import

application = bottle.default_app()
