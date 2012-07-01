from webob import Request, Response
from pprint import pprint


def app(environ, start_response):
    req = Request(environ)
    pprint(req)
    if req.path_info=='/' and req.method=='GET':
        page=open('page.html').read()
        resp = Response(page, "200 OK", [ ("Content-type", "text/html"), ])
        return resp(environ, start_response)
    if req.path_info=='/page.js' and req.method=='GET':
        page=open('page.js').read()
        resp = Response(page, "200 OK", [ ("Content-type", "text/javascript"), ])
        return resp(environ, start_response)
    else:
        resp = Response()
        return resp(environ, start_response)
    
if __name__ == '__main__':
    from paste import httpserver
    httpserver.serve(app, host='127.0.0.1', port='8080')
