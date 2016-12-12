import os

import pypn


token = os.environ.get('TESTING_GCM_TOKEN')
token_bad = 'bad-token'
topic = 'global'
player_ids = [os.environ.get('TESTING_OS_PLAYER_IDS')]

data = {
    "body": "Hello world!",
    "title": "Yahoooo",
    "apns_launch_image": "default",
    "apns_badge": 1,
    "sound": 'x',
    "apns_content_available": 1,
    "apns_category": "My_custom_x",
    "apns_mutable_content": True,
    "priority": "high",
}

topic_data = data.copy()
data['data'] = {'Nick': 'Mario'}

gcmp = pypn.Notification(pypn.GCM)

result = gcmp.send(token, data)

result = gcmp.send(topic, topic_data)

result = gcmp.send([token_bad, token], data)

apns = pypn.Notification(pypn.APNS)

token = os.environ.get('TESTING_APNS_TOKEN')

response = apns.send(token, data)
print(response.status_code)
print(response.reason)

onesignal = pypn.Notification(pypn.OS)

result = onesignal.send(player_ids, data)

# import pdb; pdb.set_trace()


# apns.send([token_bad, token], data)
