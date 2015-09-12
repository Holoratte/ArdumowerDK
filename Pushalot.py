
from urllib import urlencode
from httplib import HTTPSConnection, HTTPException
from ssl import SSLError


def send(pushalot_authorizationtoken, pushalot_body = 'something happend', pushalot_title = 'Sheep Sheep'):

    http_handler = HTTPSConnection("pushalot.com")
    data = {'AuthorizationToken': pushalot_authorizationtoken,
            'Title': pushalot_title.encode('utf-8'),
            'Body': pushalot_body.encode('utf-8') }

    try:

    	http_handler.request("POST",
    	                        "/api/sendmessage",
    	                        headers = {'Content-type': "application/x-www-form-urlencoded"},
                                body = urlencode(data))
    except (SSLError, HTTPException):
    	print("Pushalot notification failed.")

    response = http_handler.getresponse()


    return response




# testing
if __name__ == '__main__':
    send('xxxxxxxxxxx', "this is a test", "test")
##    response = send('xxxxxxxxxxxxxxx', "this is a test", "test")
##    print(response.status, response.reason)

