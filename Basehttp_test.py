import time
import BaseHTTPServer
import pprint


HOST_NAME = 'ecp-20130128' # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 9000 # Maybe set this to 9000.


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
    def do_POST(self):
        """Respond to a POST request."""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        '''
        self.wfile.write("<html><head><title>Title goes here.</title></head>")
        self.wfile.write("<body><p>This is a test.</p>")
        self.wfile.write("<body><form action='.' method='POST'><input type='text' name='xxxxxxxxxxxx' value='0000000000000000000000' /><input type='submit' /></form><p>This is a test.</p>")
        self.wfile.write("<p>POST: You accessed path: %s</p>" % self.path)
        self.wfile.write("</body></html>")
        '''
        print self.command
        print self.request
        line =  self.rfile.readlines()
        for Eachline in line:
                print Eachline
                
#       pprint (vars(self))
#       self.wfile.write('[%s] %s' %(time.ctime(),self.rfile.readline()))
        
    def do_GET(self):
        print self.server
        print self.client_address
        print self.command
        print self.request
        print self.headers
        """Respond to a GET request."""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("This is a test")
#        self.wfile.write("<html><head><title>Title goes here.</title></head>")
#        self.wfile.write("<body><p>This is a test.</p>")
        # If someone went to "http://something.somewhere.net/foo/bar/",
        # then s.path equals "/foo/bar/".
#        self.wfile.write("<p>You accessed path: %s</p>" % self.path)
#        self.wfile.write("</body></html>")

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)