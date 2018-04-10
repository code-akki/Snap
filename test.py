from pyfcm import FCMNotification
import datetime
import json
push_service = FCMNotification(api_key="AAAARXD4tc8:APA91bF--czU1L658-tCk8E4sQaguamIFapxjiZ1pFqzjIPj6j5hG-_yE__DPXLgq_tt_oHmE0fonw1HzpTwy90QMsVv4-okWJqPHZHfsqAtvJFiV902AUm4yQt1bipcETlzL0YsjbWB")
registration_id = "cb09uII_1E0:APA91bF0EIEggPhVEAoaFXPfxWSVi1tXfT8gz3xMWr1pl2mxeQDQrDC1yyodVIw_8VJLjuwISQ0FgDQ-hn9H-mGa6WAhfQfPkLmuSUvoO6-l1uYLA49HPnQzhiw00R4Z92DuR-mR8unH"
# message_title = "Notification"
# message_body = "This is from test.py"
data_message={
    "\"Id\"": "\"dakhsgdka\"",
    "\"message_title\"": "\"Knock Knock\"",
    "\"message_body\"": "\"Somebody is at your door\"",
    #"time_stamp": str(datetime.datetime.now().time())
    "\"time_stamp\"":"\"123456789\""
}
result = push_service.notify_single_device(registration_id=registration_id, data_message=data_message)
print(result)