"""Local Streamlit launcher with the light canvas present before React starts.

Only the root HTML is decorated; Streamlit owns assets, sockets and processing.
No installed dependency files are changed.
"""
import streamlit as st
import os
from starlette.routing import Route
from starlette.responses import JSONResponse
from anonimizar_local import VERSION
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import HTMLResponse


INITIAL_CANVAS = """<style id="anon-initial-canvas">
html,body,#root,.stApp,[data-testid="stAppViewContainer"] {
  background:#1c1c1b !important; color-scheme:dark;
}
header,.stAppHeader,.stAppToolbar,.stToolbarActions,
[data-testid="stHeader"],[data-testid="stToolbar"],
[data-testid="stStatusWidget"] { display:none !important; }
</style>"""


class InitialCanvasMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        is_document = request.method == 'GET' and request.url.path == '/'
        if not is_document:
            return await call_next(request)
        # A previously cached, undecorated shell must not be reused via a 304.
        request.scope['headers'] = [
            (key, value) for key, value in request.scope['headers']
            if key.lower() not in (b'if-none-match', b'if-modified-since', b'range')
        ]
        response = await call_next(request)
        if response.status_code != 200 or 'text/html' not in response.headers.get('content-type', ''):
            return response
        body = b''.join([chunk async for chunk in response.body_iterator])
        html = body.decode('utf-8').replace('</head>', INITIAL_CANVAS + '</head>', 1)
        headers = {key: value for key, value in response.headers.items()
                   if key.lower() not in ('content-length', 'etag', 'last-modified')}
        headers['cache-control'] = 'no-cache'
        return HTMLResponse(html, headers=headers, background=response.background)


async def identity(request):
    return JSONResponse({'product': 'Anonimizar', 'version': VERSION,
                         'instance': os.environ.get('ANONIMIZAR_INSTANCE', 'development')})


app = st.App('presidio_streamlit.py', routes=[Route('/anonimizar/identity', identity)],
             middleware=[Middleware(InitialCanvasMiddleware)])

if __name__ == '__main__':
    app.run()
