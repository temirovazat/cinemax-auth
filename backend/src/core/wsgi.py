from gevent import monkey

monkey.patch_all()

from secrets import token_hex

from flask import g, request

from manage import create_app

app = create_app()


@app.before_request
def before_request():
    """Add `request-id` information to the log for each request."""
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        request_id = token_hex(16)
    g.request_id = request_id
    app.logger.info('logging')
