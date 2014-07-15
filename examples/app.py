#-*-coding:utf-8-*-

def app(environ, start_response):
    status = '200 OK'
    response_string = 'Hello World'
    response_headers = [
        ('Content-Type', 'text/plain'),
        ('Content-Length', len(response_string)),
    ]
    start_response(status, response_headers)
    return [response_string]
