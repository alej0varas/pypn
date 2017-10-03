import os
import re

try:
    import apns2
    APNS = 'apns'
except ImportError:
    APNS = None
try:
    import gcm
    GCM = 'gcm'
except ImportError:
    GCM = None
try:
    import yaosac
    OS = 'onesignal'
except ImportError:
    OS = None
DUMMY = 'dummy'


four_weeks_in_seconds = 40320  # 60 * 60 * 24 * 7 * 4


class APNsProvider:
    def __init__(self):
        mode = os.environ.get('APNS_MODE', "dev")
        cert_file = os.environ.get('APNS_CERT_FILE')
        certificate_password = os.environ.get('APNS_CERT_PASSWORD', '')

        def get_password():
            return certificate_password

        self.client = apns2.APNSClient(client_cert=cert_file, mode=mode, password=get_password)

    def send(self, to, notification):
        notification_kwargs = {}
        notification_kwargs['priority'] = notification.pop('priority')

        if isinstance(notification['alert'], dict):
            alert = apns2.PayloadAlert(**notification.pop('alert'))
            payload = apns2.Payload(alert=alert, **notification)
        else:
            payload = apns2.Payload(**notification)
        notification = apns2.Notification(payload=payload, **notification_kwargs)

        result = []

        if isinstance(to, (list, tuple)):
            for t in to:
                result.append(self.client.push(device_token=t, n=notification))
        else:
            result = self.client.push(device_token=to, n=notification)

        return result


class GCMProvider:
    topic_patern = re.compile('[a-zA-Z0-9-_.~%]+')
    dry_run = bool(int(os.environ.get('GCM_DRY_RUN', 1)))

    def __init__(self):
        api_key = os.environ.get('GCM_SERVER_KEY')
        _logging = bool(os.environ.get('GCM_LOGGING'))
        self.client = gcm.GCM(api_key, debug=_logging)

    def send(self, to, notification):
        notification['dry_run'] = self.dry_run
        if isinstance(to, (list, tuple)):
            result = self.client.json_request(registration_ids=to, **notification)
        elif re.fullmatch(self.topic_patern, to):
            result = self.client.send_topic_message(topic=to, **notification)
        else:
            result = self.client.send_to_message(to=to, **notification)
        return result


class OneSignalProvider:
    def send(self, to, data):
        # `contents` and `template_id` can be used, if `contents` is
        # present it has precedence and the `template_id` is not used
        # by OneSignal.
        contents = data.pop('contents', None)
        template_id = data.pop('template_id', None)
        data.update({'include_player_ids': to})
        response = yaosac.client.create_notification(
            contents=contents, template_id=template_id, **data)
        return response


class DummyProvider:
    def send(self, to, data):
        return to, data


class Notification:
    def __init__(self, provider):
        self.provider_name = self.validate_provider(provider)
        if not self.provider_name:
            raise AttributeError('%s is not a valid provider')
        self.provider = providers[self.provider_name]()

    def send(self, to, kwargs=None):
        # result = self.provider.send(to, **kwargs)
        self.kwargs = kwargs
        result = self.provider.send(to, self.get_args_for_provider())
        return result

    def get_args_for_dummy(self):
        return self.kwargs

    def get_args_for_provider(self):
        method_name = 'get_args_for_' + self.provider_name.lower()
        method = getattr(self, method_name, None)
        if method is None:
            return
        kwargs = method()
        return kwargs

    def get_args_for_apns(self):
        priorities = {'normal': "5", 'high': "10"}
        kwargs = {}
        alert = {}

        # Shared
        body = self.kwargs.get('body')
        kwargs['sound'] = self.kwargs.get('sound')
        kwargs['priority'] = priorities.get(self.kwargs.get('priority'))
        alert['title'] = self.kwargs.get('title')

        kwargs['badge'] = self.kwargs.get('apns_badge')
        kwargs['content_available'] = self.kwargs.get('apns_content_available')
        kwargs['category'] = self.kwargs.get('apns_category')
        kwargs['mutable_content'] = self.kwargs.get('apns_mutable_content')

        alert['title_loc_key'] = self.kwargs.get('apns_alert_title_loc_key')
        alert['title_loc_args'] = self.kwargs.get('apns_alert_title_loc_args')
        alert['loc_key'] = self.kwargs.get('apns_alert_loc_key')
        alert['loc_args'] = self.kwargs.get('apns_alert_loc_args')
        alert['action_loc_key'] = self.kwargs.get('apns_alert_action_loc_key')
        alert['launch_image'] = self.kwargs.get('apns_alert_launch_image')

        kwargs['custom'] = self.kwargs.get('apns_custom')

        if any(alert.values()):
            alert['body'] = body
            kwargs['alert'] = alert

        else:
            kwargs['alert'] = body

        return kwargs

    def get_args_for_gcm(self):
        kwargs = {}
        # Get payload
        kwargs['data'] = self.kwargs.get('gcm_data')

        kwargs['notification'] = {}
        # Shared
        kwargs['notification']['body'] = self.kwargs.get('body')
        kwargs['notification']['sound'] = self.kwargs.get('sound')
        kwargs['notification']['title'] = self.kwargs.get('title')
        kwargs['priority'] = self.kwargs.get('priority')
        # Only GCM
        kwargs['notification']['icon'] = self.kwargs.get('gcm_notification_icon')
        kwargs['notification']['tag'] = self.kwargs.get('gcm_notification_tag')
        kwargs['notification']['color'] = self.kwargs.get('gcm_notification_color')
        kwargs['notification']['click_action'] = self.kwargs.get('gcm_notification_click_action')
        kwargs['notification']['body_loc_key'] = self.kwargs.get('gcm_notification_body_loc_key')
        kwargs['notification']['body_loc_args'] = self.kwargs.get('gcm_notification_body_loc_args')
        kwargs['notification']['title_loc_key'] = self.kwargs.get('gcm_notification_title_loc_key')
        kwargs['notification']['title_loc_args'] = self.kwargs.get('gcm_notification_title_loc_args')
        # Get options
        kwargs['collapse_key'] = self.kwargs.get('gcm_option_collapse_key')
        kwargs['content_available'] = self.kwargs.get('gcm_option_content_available')
        kwargs['delay_while_idle'] = self.kwargs.get('gcm_option_delay_while_idle')
        kwargs['time_to_live'] = self.kwargs.get('gcm_option_time_to_live', four_weeks_in_seconds)
        kwargs['restricted_package_name'] = self.kwargs.get('gcm_option_restricted_package_name')

        return kwargs

    def get_args_for_onesignal(self):
        kwargs = {}
        if 'os_template_id' in self.kwargs and self.kwargs['os_template_id'] is not None:
            kwargs['template_id'] = self.kwargs['os_template_id']
        if 'title' in self.kwargs:
            kwargs['heading'] = self.kwargs['title']
        if 'body' in self.kwargs:
            kwargs['contents'] = self.kwargs['body']
        if 'data' in self.kwargs:
            kwargs['data'] = self.kwargs['data']

        return kwargs

    def validate_provider(self, provider):
        return provider in providers and provider


providers = {DUMMY: DummyProvider}
if APNS is not None:
    providers.update({APNS: APNsProvider})
if GCM is not None:
    providers.update({GCM: GCMProvider})
if OS is not None:
    providers.update({OS: OneSignalProvider})
