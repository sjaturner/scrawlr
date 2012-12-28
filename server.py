from webob import Request, Response
from pprint import pprint
import sys

def app(environ, start_response):
    req = Request(environ)
    pprint(req)
    if req.path_info=='/json' and req.method=='POST':
        open(sys.argv[1],'w').write(req.body)
        resp = Response(None, "200 OK", [ ("Content-type", "text/html"), ])
        return resp(environ, start_response)
    if req.path_info=='/json' and req.method=='GET':
        page=open(sys.argv[1]).read()
        resp = Response(page, "200 OK", [ ("Content-type", "text/javascript"), ])
        return resp(environ, start_response)
    elif req.path_info=='/' and req.method=='GET':
        page=open('page.html').read()
        resp = Response(page, "200 OK", [ ("Content-type", "text/html"), ])
        return resp(environ, start_response)
    elif req.path_info=='/page.js' and req.method=='GET':
        page=open('page.js').read()
        resp = Response(page, "200 OK", [ ("Content-type", "text/javascript"), ])
        return resp(environ, start_response)
    elif req.path_info=='/jquery.min.js' and req.method=='GET':
        page=open('jquery.min.js').read()
        resp = Response(page, "200 OK", [ ("Content-type", "text/javascript"), ])
        return resp(environ, start_response)
    else:
        resp = Response()
        return resp(environ, start_response)
    
if __name__ == '__main__':
    from paste import httpserver
    httpserver.serve(app, host='0.0.0.0', port='8080')
