package cdi.gentek.com.snap;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.support.v4.content.LocalBroadcastManager;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.TextUtils;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import com.bumptech.glide.Glide;
import com.firebase.ui.storage.images.FirebaseImageLoader;
import com.google.firebase.database.ChildEventListener;
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;
import com.google.firebase.messaging.FirebaseMessaging;
import com.google.firebase.storage.FirebaseStorage;
import com.google.firebase.storage.StorageReference;

import org.eclipse.paho.android.service.MqttAndroidClient;
//import org.eclipse.paho.client.mqttv3.DisconnectedBufferOptions;
import org.eclipse.paho.client.mqttv3.IMqttActionListener;
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
//import org.eclipse.paho.client.mqttv3.IMqttMessageListener;
import org.eclipse.paho.client.mqttv3.IMqttToken;
//import org.eclipse.paho.client.mqttv3.MqttCallbackExtended;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.json.JSONObject;

import java.io.UnsupportedEncodingException;
import java.lang.reflect.Array;

import cdi.gentek.com.snap.app.Config;
import cdi.gentek.com.snap.utils.NotificationUtils;
import me.aflak.libraries.callback.FingerprintDialogSecureCallback;
import me.aflak.libraries.dialog.FingerprintDialog;
import me.aflak.libraries.utils.FingerprintToken;

public class MainActivity extends AppCompatActivity  implements FingerprintDialogSecureCallback,MqttCallback{

    private static final String TAG = MainActivity.class.getSimpleName();
    private BroadcastReceiver mBroadcastReceiver;

    MqttAndroidClient mqttAndroidClient;

    final String serverUri = "tcp://172.16.73.4:1883";

    String clientId = "SnapAndroidClient";
    MqttAndroidClient client;
    final String subscriptionTopicAuth = "snap/home/door1/auth";
    final String subscriptionTopicKey = "snap/home/door1/key";
    final String publishTopicAndroid = "snap/home/door1/android";
    final String publishMessage="user1";
    String image_id;
    FirebaseStorage storage;
    ImageView imageView;
    TextView statusView;
    Button authYesButton, authNoButton;
    static String guestId;
    DatabaseReference mDatabase;
    static boolean locked_status;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        statusView=(TextView)findViewById(R.id.locked_status);
        imageView=(ImageView)findViewById(R.id.image_id);
        authYesButton=(Button)findViewById(R.id.auth_yes);
        authNoButton=(Button)findViewById(R.id.auth_no);
        storage = FirebaseStorage.getInstance();
        mDatabase= FirebaseDatabase.getInstance().getReference();
        mDatabase.child("status").child("locked").addValueEventListener(new ValueEventListener() {
            @Override
            public void onDataChange(DataSnapshot dataSnapshot) {
                locked_status=dataSnapshot.getValue(Boolean.class);
                if(locked_status){
                    statusView.setText("Locked");
                }else {
                    statusView.setText("Unlocked");
                }
            }

            @Override
            public void onCancelled(DatabaseError databaseError) {
                Log.d("MainActivity","error reading data");
            }
        });

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
                    if(TextUtils.isEmpty(image_id)){}
                    else{
                        StorageReference storageRef = storage.getReference();
                        // Create a reference with an initial file path and name
                        StorageReference pathReference = storageRef.child(image_id);
                        Glide.with(getApplicationContext() /* context */)
                                .using(new FirebaseImageLoader())
                                .load(pathReference)
                                .into(imageView);
                        authYesButton.setVisibility(View.VISIBLE);
                        authNoButton.setVisibility(View.VISIBLE);

                    }
                    Toast.makeText(getApplicationContext(),"Push Notification: "+image_id,Toast.LENGTH_LONG).show();
                    //textMessage.setText(message);
                }
            }
        };
        displayFirebaseId();

        authYesButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                // publish json data in /snap/home/door1/auth as yes
                publishMessage("snap/home/door1/auth",guestId+"_True_user1");
            }
        });

        authNoButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                // publish json data in /snap/home/door1/auth as no

                publishMessage("snap/home/door1/auth",guestId+"_False_user1");
            }
        });
//
//        clientId = clientId;
//
//        mqttAndroidClient = new MqttAndroidClient(getApplicationContext(), serverUri, clientId);
//        mqttAndroidClient.setCallback(new MqttCallbackExtended() {
//            @Override
//            public void connectComplete(boolean reconnect, String serverURI) {
//
//                if (reconnect) {
//                    // Because Clean Session is true, we need to re-subscribe
//                    subscribeToTopic();
//                } else {
////                    addToHistory("Connected to: " + serverURI);
//                    Log.d("MainActivity","connected");
//                }
//            }

//            @Override
//            public void connectionLost(Throwable cause) {
////                addToHistory("The Connection was lost.");
//            }
//
//            @Override
//            public void messageArrived(String topic, MqttMessage message) throws Exception {
////                addToHistory("Incoming message: " + new String(message.getPayload()));
//                if(topic.equals(subscriptionTopicAuth)){
//                    //authorize the person and publish
//                    String arr[]= new String(message.getPayload()).split("_");
//                    guestId=arr[0];
//
//                }
//                else if(topic.equals(subscriptionTopicKey)){
//                    //save the key in a file after encrypting
//
//                }
//            }
//
//            @Override
//            public void deliveryComplete(IMqttDeliveryToken token) {
//
//            }
//        });
//
//        MqttConnectOptions mqttConnectOptions = new MqttConnectOptions();
//        mqttConnectOptions.setAutomaticReconnect(true);
//        mqttConnectOptions.setCleanSession(true);
//
//        try {
//            //addToHistory("Connecting to " + serverUri);
//            mqttAndroidClient.connect(mqttConnectOptions, null, new IMqttActionListener() {
//                @Override
//                public void onSuccess(IMqttToken asyncActionToken) {
////                    DisconnectedBufferOptions disconnectedBufferOptions = new DisconnectedBufferOptions();
////                    disconnectedBufferOptions.setBufferEnabled(true);
////                    disconnectedBufferOptions.setBufferSize(100);
////                    disconnectedBufferOptions.setPersistBuffer(false);
////                    disconnectedBufferOptions.setDeleteOldestMessages(false);
////                    mqttAndroidClient.setBufferOpts(disconnectedBufferOptions);
//                    subscribeToTopic();
//                    Log.d("MainActivity","connected");
//                }
//
//                @Override
//                public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
////                    addToHistory("Failed to connect to: " + serverUri);
//                    Log.d("MainActivity","cannot connected");
//                }
//            });
//
//
//        } catch (MqttException ex){
//            ex.printStackTrace();
//        }


        String clientId = MqttClient.generateClientId();
        client =
                new MqttAndroidClient(this.getApplicationContext(), "tcp://172.16.73.39:1883",
                        clientId);

        try {
            MqttConnectOptions options = new MqttConnectOptions();
            options.setMqttVersion(MqttConnectOptions.MQTT_VERSION_3_1);
            IMqttToken token = client.connect(options);
            token.setActionCallback(new IMqttActionListener() {
                @Override
                public void onSuccess(IMqttToken asyncActionToken) {
                    // We are connected
                    Log.d(TAG, "onSuccess");
                    try{
                        client.subscribe("snap/home/door1/auth", 2);
                    }catch (MqttException e){
                        e.printStackTrace();
                    }
                }

                @Override
                public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
                    // Something went wrong e.g. connection timeout or firewall problems
                    Log.d(TAG, "onFailure");

                }
            });
        } catch (MqttException e) {
            e.printStackTrace();
        }

//        try {
//            IMqttToken subToken = client.subscribe("snap/home/door1/auth", 2);
//            subToken.setActionCallback(new IMqttActionListener() {
//                @Override
//                public void onSuccess(IMqttToken asyncActionToken) {
//                    // The message was published
//                }
//
//                @Override
//                public void onFailure(IMqttToken asyncActionToken,
//                                      Throwable exception) {
//                    // The subscription could not be performed, maybe the user was not
//                    // authorized to subscribe on the specified topic e.g. using wildcards
//
//                }
//            });
//        } catch (MqttException e) {
//            e.printStackTrace();
//        }

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
//        try {
//
//            mqttAndroidClient.subscribe(subscriptionTopicAuth,2);
//            mqttAndroidClient.subscribe(subscriptionTopicKey,2);
//
//            // THIS DOES NOT WORK!
//            mqttAndroidClient.subscribe(subscriptionTopicAuth, 0, new IMqttMessageListener() {
//                @Override
//                public void messageArrived(String topic, MqttMessage message) throws Exception {
//                    // message Arrived!
//                    System.out.println("Message: " + topic + " : " + new String(message.getPayload()));
//                }
//            });
//
//            mqttAndroidClient.subscribe(subscriptionTopicKey, 0, new IMqttMessageListener() {
//                @Override
//                public void messageArrived(String topic, MqttMessage message) throws Exception {
//                    // message Arrived!
//                    System.out.println("Message: " + topic + " : " + new String(message.getPayload()));
//                }
//            });
//
//        } catch (MqttException ex){
//            System.err.println("Exception whilst subscribing");
//            ex.printStackTrace();
//        }
    }

    public void publishMessage(String topic,String messagePublish){

//        try {
//            MqttMessage message = new MqttMessage();
//            message.setPayload(messagePublish.getBytes());
//            mqttAndroidClient.publish(topic, message);
//            //addToHistory("Message Published");
//            if(!mqttAndroidClient.isConnected()){
////                addToHistory(mqttAndroidClient.getBufferedMessageCount() + " messages in buffer.");
//            }
//        } catch (MqttException e) {
//            System.err.println("Error Publishing: " + e.getMessage());
//            e.printStackTrace();
//        }

        byte[] encodedPayload = new byte[0];
        try {
            encodedPayload = messagePublish.getBytes("UTF-8");
            MqttMessage message = new MqttMessage(encodedPayload);
            client.publish(topic, message);
        } catch (UnsupportedEncodingException | MqttException e) {
            e.printStackTrace();
        }
    }

    @Override
    public void onAuthenticationSucceeded() {
        if(locked_status)
            publishMessage("snap/home/door1/open","yes_user1");
    }

    @Override
    public void onAuthenticationCancel() {

    }

    @Override
    public void onNewFingerprintEnrolled(FingerprintToken token) {

    }

    @Override
    protected void onResume() {
        super.onResume();

        //register complete FCM receiver
        LocalBroadcastManager.getInstance(this).registerReceiver(mBroadcastReceiver,new IntentFilter(Config.REGISTRATION_COMPLETE));

        //register push message
        LocalBroadcastManager.getInstance(this).registerReceiver(mBroadcastReceiver,new IntentFilter(Config.PUSH_NOTIFICATION));

        //clear notification when app is opened
        NotificationUtils.clearNotification(getApplicationContext());
        if(FingerprintDialog.isAvailable(this)) {
            FingerprintDialog.initialize(this)
                    .title("Fingerprint Authentication")
                    .message("Please auhtenticate using fingerprint")
                    .callback(this, "KeyName1")
                    .show();
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        LocalBroadcastManager.getInstance(this).unregisterReceiver(mBroadcastReceiver);
    }

    @Override
    public void connectionLost(Throwable cause) {

    }

    @Override
    public void messageArrived(String topic, MqttMessage message) throws Exception {
        if(topic.equals(subscriptionTopicAuth)){
            //authorize the person and publish
          String arr[]= new String(message.getPayload()).split("_");
                    guestId=arr[0];
         }

    }

    @Override
    public void deliveryComplete(IMqttDeliveryToken token) {

    }
}