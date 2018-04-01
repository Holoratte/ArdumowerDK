import requests
import json

def send(api_key, notification_message = 'something happend', notification_title = 'Sheep Sheep'):
    url = "https://www.notifymydevice.com/push"
    data = {"ApiKey": api_key, "PushTitle": notification_title,"PushText": notification_message}
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    if r.status_code == 200:
        print 'Notification sent!'
    else:
        print 'Error while sending notificaton!'

    return r


if __name__ == '__main__':
    response = send('xxxxxxxxx', "this is a test", "test")
    print(response.status_code)