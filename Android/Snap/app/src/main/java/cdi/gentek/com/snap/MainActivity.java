package cdi.gentek.com.snap;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.TextUtils;
import android.util.Log;
import android.widget.Toast;

import com.google.firebase.messaging.FirebaseMessaging;

import org.eclipse.paho.android.service.MqttAndroidClient;
import org.eclipse.paho.client.mqttv3.DisconnectedBufferOptions;
import org.eclipse.paho.client.mqttv3.IMqttActionListener;
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.IMqttMessageListener;
import org.eclipse.paho.client.mqttv3.IMqttToken;
import org.eclipse.paho.client.mqttv3.MqttCallbackExtended;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;

import cdi.gentek.com.snap.app.Config;
import me.aflak.libraries.callback.FingerprintDialogSecureCallback;
import me.aflak.libraries.dialog.FingerprintDialog;
import me.aflak.libraries.utils.FingerprintToken;

public class MainActivity extends AppCompatActivity  implements FingerprintDialogSecureCallback{

    private static final String TAG = MainActivity.class.getSimpleName();
    private BroadcastReceiver mBroadcastReceiver;

    MqttAndroidClient mqttAndroidClient;

    final String serverUri = "tcp://172.16.73.39:1883";

    String clientId = "SnapAndroidClient";
    final String subscriptionTopicAuth = "snap/home/door1/auth";
    final String subscriptionTopicKey = "snap/home/door1/key";
    final String publishTopicAndroid = "snap/home/door1/android";
    final String publishMessage="User1";
    String image_id;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mBroadcastReceiver = new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                //checking for type of intent filter
                if(intent.getAction().equals(Config.REGISTRATION_COMPLETE)) {
                    //successfully registered, subscribe to global topic
                    FirebaseMessaging.getInstance().subscribeToTopic(Config.TOPIC_GLOBAL);
                    displayFirebaseId();
                }else if (intent.getAction().equals(Config.PUSH_NOTIFICATION)){
                    image_id = intent.getStringExtra("id");
                    Toast.makeText(getApplicationContext(),"Push Notification: "+image_id,Toast.LENGTH_LONG).show();
                    //textMessage.setText(message);
                }
            }
        };
        displayFirebaseId();

        clientId = clientId + System.currentTimeMillis();

        mqttAndroidClient = new MqttAndroidClient(getApplicationContext(), serverUri, clientId);
        mqttAndroidClient.setCallback(new MqttCallbackExtended() {
            @Override
            public void connectComplete(boolean reconnect, String serverURI) {

                if (reconnect) {
                    // Because Clean Session is true, we need to re-subscribe
                    subscribeToTopic();
                } else {
//                    addToHistory("Connected to: " + serverURI);
                }
            }

            @Override
            public void connectionLost(Throwable cause) {
//                addToHistory("The Connection was lost.");
            }

            @Override
            public void messageArrived(String topic, MqttMessage message) throws Exception {
//                addToHistory("Incoming message: " + new String(message.getPayload()));
                if(topic.equals(subscriptionTopicAuth)){
                    //authorize the person and publish
                }
                else if(topic.equals(subscriptionTopicKey)){
                    //save the key in a file after encrypting
                }
            }

            @Override
            public void deliveryComplete(IMqttDeliveryToken token) {

            }
        });

        MqttConnectOptions mqttConnectOptions = new MqttConnectOptions();
        mqttConnectOptions.setAutomaticReconnect(true);
        mqttConnectOptions.setCleanSession(false);

        try {
            //addToHistory("Connecting to " + serverUri);
            mqttAndroidClient.connect(mqttConnectOptions, null, new IMqttActionListener() {
                @Override
                public void onSuccess(IMqttToken asyncActionToken) {
                    DisconnectedBufferOptions disconnectedBufferOptions = new DisconnectedBufferOptions();
                    disconnectedBufferOptions.setBufferEnabled(true);
                    disconnectedBufferOptions.setBufferSize(100);
                    disconnectedBufferOptions.setPersistBuffer(false);
                    disconnectedBufferOptions.setDeleteOldestMessages(false);
                    mqttAndroidClient.setBufferOpts(disconnectedBufferOptions);
                    subscribeToTopic();
                }

                @Override
                public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
//                    addToHistory("Failed to connect to: " + serverUri);
                }
            });


        } catch (MqttException ex){
            ex.printStackTrace();
        }

        if(FingerprintDialog.isAvailable(this)) {
            FingerprintDialog.initialize(this)
                    .title("Fingerprint Authentication")
                    .message("Please auhtenticate using fingerprint")
                    .callback(this, "KeyName1")
                    .show();
        }
    }

    private void displayFirebaseId() {
        SharedPreferences pref = getApplicationContext().getSharedPreferences(Config.SHARED_PREF, 0);
        String regId = pref.getString("regId", null);

        Log.e(TAG, "Firebase reg id: " + regId);

    }

    public void subscribeToTopic(){
        try {

            mqttAndroidClient.subscribe(subscriptionTopicAuth,2);
            mqttAndroidClient.subscribe(subscriptionTopicKey,2);

            // THIS DOES NOT WORK!
            mqttAndroidClient.subscribe(subscriptionTopicAuth, 0, new IMqttMessageListener() {
                @Override
                public void messageArrived(String topic, MqttMessage message) throws Exception {
                    // message Arrived!
                    System.out.println("Message: " + topic + " : " + new String(message.getPayload()));
                }
            });

            mqttAndroidClient.subscribe(subscriptionTopicKey, 0, new IMqttMessageListener() {
                @Override
                public void messageArrived(String topic, MqttMessage message) throws Exception {
                    // message Arrived!
                    System.out.println("Message: " + topic + " : " + new String(message.getPayload()));
                }
            });

        } catch (MqttException ex){
            System.err.println("Exception whilst subscribing");
            ex.printStackTrace();
        }
    }

    public void publishMessage(String topic,String messagePublish){

        try {
            MqttMessage message = new MqttMessage();
            message.setPayload(messagePublish.getBytes());
            mqttAndroidClient.publish(topic, message);
            //addToHistory("Message Published");
            if(!mqttAndroidClient.isConnected()){
//                addToHistory(mqttAndroidClient.getBufferedMessageCount() + " messages in buffer.");
            }
        } catch (MqttException e) {
            System.err.println("Error Publishing: " + e.getMessage());
            e.printStackTrace();
        }
    }

    @Override
    public void onAuthenticationSucceeded() {

    }

    @Override
    public void onAuthenticationCancel() {

    }

    @Override
    public void onNewFingerprintEnrolled(FingerprintToken token) {

    }
}

