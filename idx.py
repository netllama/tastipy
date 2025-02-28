from os import chdir, path

# Change working directory so relative paths (and template lookup) work again
chdir(path.dirname(__file__))

import bottle  # noqa: C0413

application = bottle.default_app()
