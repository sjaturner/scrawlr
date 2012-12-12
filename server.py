from webob import Request, Response
from pprint import pprint

def prepro(file):
    hash_include='#include'
    ret=''
    for line in open(file):
        if hash_include in line:
            ret+=prepro(line.split(hash_include)[1].split('"')[1])
        else:
            ret+=line
    return ret

def app(environ, start_response):
    req = Request(environ)
    pprint(req)
    if req.path_info=='/' and req.method=='GET':
        page=open('page.html').read()
        resp = Response(page, "200 OK", [ ("Content-type", "text/html"), ])
        return resp(environ, start_response)
    if req.path_info=='/page.js' and req.method=='GET':
        page=prepro('ui.js')
        resp = Response(page, "200 OK", [ ("Content-type", "text/javascript"), ])
        return resp(environ, start_response)
    if req.path_info=='/jquery.min.js' and req.method=='GET':
        page=open('jquery.min.js').read()
        resp = Response(page, "200 OK", [ ("Content-type", "text/javascript"), ])
        return resp(environ, start_response)
    else:
        resp = Response()
        return resp(environ, start_response)
    
if __name__ == '__main__':
    from paste import httpserver
    httpserver.serve(app, host='0.0.0.0', port='8080')
