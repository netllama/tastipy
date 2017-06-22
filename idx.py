from os import chdir, path

# Change working directory so relative paths (and template lookup) work again
chdir(path.dirname(__file__))

import bottle
import hello

application = bottle.default_app()
