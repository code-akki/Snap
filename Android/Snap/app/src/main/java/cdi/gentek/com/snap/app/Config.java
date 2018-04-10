package cdi.gentek.com.snap.app;

/**
 * Created by apple on 10/03/18.
 */

public class Config {
    // global topic to receive app wide push notification
    public static final String TOPIC_GLOBAL = "global";

    //broadcast receive intent filter
    public static final String REGISTRATION_COMPLETE= "registrationComplete";
    public static final String PUSH_NOTIFICATION = "pushNotification";

    // id to handle notification in the tray
    public static final int NOTIFICATION_ID = 100;


    public static final String SHARED_PREF = "fcm_data";
    public static final String SHARED_PREF_BACKUP_KEY = "prefs_data";
}
