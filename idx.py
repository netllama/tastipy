"""
    Generates toplevel index.
"""
from os import chdir, path

# Change working directory so relative paths (and template lookup) work again
chdir(path.dirname(__file__))

import bottle  # pylint: disable=C0413
import tastiapp

application = bottle.default_app()
