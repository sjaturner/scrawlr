from webob import Request, Response
from pprint import pprint

def app(environ, start_response):
    req = Request(environ)
    pprint(req)
    if req.path_info=='/' and req.method=='GET':
        resp = Response("Hello World!", "200 OK", [ ("Content-type", "text/plain"), ])
        return resp(environ, start_response)
    else:
        resp = Response()
        return resp(environ, start_response)
    
if __name__ == '__main__':
    from paste import httpserver
    httpserver.serve(app, host='127.0.0.1', port='8080')
