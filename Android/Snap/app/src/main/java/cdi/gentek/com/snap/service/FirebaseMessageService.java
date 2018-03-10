package cdi.gentek.com.snap.service;

import android.content.Context;
import android.content.Intent;
import android.os.Vibrator;
import android.support.v4.content.LocalBroadcastManager;
import android.util.Log;

import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;

import org.json.JSONException;
import org.json.JSONObject;

import cdi.gentek.com.snap.MainActivity;
import cdi.gentek.com.snap.app.Config;
import cdi.gentek.com.snap.utils.NotificationUtils;

/**
 * Created by apple on 10/03/18.
 */

public class FirebaseMessageService  extends FirebaseMessagingService {
    private static final String TAG = FirebaseMessageService.class.getSimpleName();

    private NotificationUtils notificationUtils;


    @Override
    public void onMessageReceived(RemoteMessage remoteMessage) {
        Log.d(TAG,"From "+remoteMessage.getFrom());

        if(remoteMessage == null){
            return;
        }

        //check if message contains notification payload

        if(remoteMessage.getNotification()!=null){
            Log.d(TAG,"Notification "+remoteMessage.getNotification().getBody());
            handleNotification(remoteMessage.getNotification().getBody());
        }

        //check if the message has data payload
        if(remoteMessage.getData().size()>0){
            Log.d(TAG,"Data "+ remoteMessage.getData().toString());

            try {
                JSONObject json = new JSONObject(remoteMessage.getData().toString());
                handleDataMessage(json);
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }


    }

    private void handleDataMessage(JSONObject json) {
        Log.e(TAG, "push json: " + json.toString());

        try {
            JSONObject data = json.getJSONObject("data");

            String title = data.getString("title");
            String message = data.getString("message_body");
//            boolean isBackground = data.getBoolean("is_background");
//            String imageUrl = data.getString("image");
            String timestamp = data.getString("timestamp");
            String id= data.getString("id");
//            JSONObject payload = data.getJSONObject("payload");

            Log.e(TAG, "title: " + title);
            Log.e(TAG, "message: " + message);
//            Log.e(TAG, "isBackground: " + isBackground);
//            Log.e(TAG, "payload: " + payload.toString());
//            Log.e(TAG, "imageUrl: " + imageUrl);
            Log.e(TAG, "timestamp: " + timestamp);


            if (!NotificationUtils.isInBackground(getApplicationContext())) {
                // app is in foreground, broadcast the push message
                Intent pushNotification = new Intent(Config.PUSH_NOTIFICATION);
                pushNotification.putExtra("id", id);
                LocalBroadcastManager.getInstance(this).sendBroadcast(pushNotification);

                // play notification sound
                NotificationUtils notificationUtils = new NotificationUtils(getApplicationContext());
                notificationUtils.playNotificationSound();
                Vibrator v = (Vibrator) getSystemService(Context.VIBRATOR_SERVICE);
                // Vibrate for 500 milliseconds
                v.vibrate(500);
            } else {
                // app is in background, show the notification in notification tray
                Intent resultIntent;
                resultIntent = new Intent(getApplicationContext(), MainActivity.class);
                resultIntent.putExtra("id", id);
                showNotificationMessage(getApplicationContext(), title, message, timestamp, resultIntent);
            }
        } catch (JSONException e) {
            Log.e(TAG, "Json Exception: " + e.getMessage());
        } catch (Exception e) {
            Log.e(TAG, "Exception: " + e.getMessage());
        }
    }

    private void showNotificationMessage(Context context, String title, String message, String timestamp, Intent intent) {
        notificationUtils = new NotificationUtils(context);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        notificationUtils.showNotificationMessage(title, message, timestamp, intent);
    }

    private void handleNotification(String body) {

        if(!NotificationUtils.isInBackground(getApplicationContext())){
            //app is in foreground, broadcast the push message
            Intent pushNotification = new Intent(Config.PUSH_NOTIFICATION);
            pushNotification.putExtra("message",body);
            LocalBroadcastManager.getInstance(this).sendBroadcast(pushNotification);

            //play notification sound
            NotificationUtils notificationUtils = new NotificationUtils(getApplicationContext());
            notificationUtils.playNotificationSound();
            Vibrator v = (Vibrator) getSystemService(Context.VIBRATOR_SERVICE);
            // Vibrate for 500 milliseconds
            v.vibrate(500);
        }
        else{
            //app is in background, FCM will handle internally
            //play notification sound
            NotificationUtils notificationUtils = new NotificationUtils(getApplicationContext());
            notificationUtils.playNotificationSound();
            Vibrator v = (Vibrator) getSystemService(Context.VIBRATOR_SERVICE);
            // Vibrate for 500 milliseconds
            v.vibrate(500);
        }
    }
}
