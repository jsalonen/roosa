from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from roosa import app

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(8080)
IOLoop.instance().start()