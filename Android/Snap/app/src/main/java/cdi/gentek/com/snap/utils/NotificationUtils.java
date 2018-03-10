package cdi.gentek.com.snap.utils;

import android.app.ActivityManager;
import android.app.Notification;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.media.Ringtone;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.Build;
import android.os.Vibrator;
import android.support.v4.app.NotificationCompat;
import android.text.TextUtils;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;

import cdi.gentek.com.snap.R;
import cdi.gentek.com.snap.app.Config;

/**
 * Created by apple on 10/03/18.
 */

public class NotificationUtils {
    private static String TAG = NotificationUtils.class.getSimpleName();

    private Context mContext;

    public NotificationUtils(Context context){
        mContext=context;
    }

//    public void showNotificationMessage(String title, String message, String timestamp, Intent intent){
//        showNotificationMessage(title, message, timestamp, intent, null);
//    }

    public void showNotificationMessage(final String title, final String message, final String timestamp, Intent intent){
        //Check for empty push message

        if(TextUtils.isEmpty(message))
            return;

        //notification icon

        final int icon = R.mipmap.ic_launcher;

        intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        final PendingIntent resultPendingIntent = PendingIntent.getActivity(
                mContext,0,intent,PendingIntent.FLAG_CANCEL_CURRENT);

        NotificationCompat.Builder mbuilder = new NotificationCompat.Builder(mContext,"channel_id");

        Uri alarmsound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);

        showSmallNotification(mbuilder,icon,title,message,timestamp,resultPendingIntent,alarmsound);
        playNotificationSound();
        Vibrator v = (Vibrator) mContext.getSystemService(Context.VIBRATOR_SERVICE);
        // Vibrate for 500 milliseconds
        v.vibrate(500);

    }

    private void showSmallNotification(NotificationCompat.Builder mbuilder, int icon, String title, String message, String timestamp, PendingIntent resultPendingIntent, Uri alarmsound) {

        NotificationCompat.InboxStyle inboxStyle = new NotificationCompat.InboxStyle();
        inboxStyle.addLine(message);
        Notification notification = mbuilder.setSmallIcon(icon).setTicker(title).setWhen(0)
                .setAutoCancel(true)
                .setContentTitle(title)
                .setSound(alarmsound)
                .setStyle(inboxStyle)
                .setWhen(getTimeMilliSec(timestamp))
                .setSmallIcon(R.mipmap.ic_launcher)
                .setContentText(message)
                .setPriority(Notification.PRIORITY_MAX)
                .setFullScreenIntent(resultPendingIntent,true)
                .build();

        NotificationManager notificationManager = (NotificationManager) mContext.getSystemService(Context.NOTIFICATION_SERVICE);
        notificationManager.notify(Config.NOTIFICATION_ID,notification);

    }

    public long getTimeMilliSec(String timestamp) {
        SimpleDateFormat dateFormat = new SimpleDateFormat("HH:mm");
        try {
            Date date = dateFormat.parse(timestamp);
            return date.getTime();
        }catch (ParseException e){
            e.printStackTrace();
        }
        return 0;
    }

    public void playNotificationSound() {
        try {
            Uri alarmsound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
            Ringtone ringtone = RingtoneManager.getRingtone(mContext,alarmsound);
            ringtone.play();
        }catch (Exception e){
            e.printStackTrace();
        }

    }

    /*
        Method to check if the app is in background*
    */

    public static boolean isInBackground(Context context){
        boolean isInBackground = true;
        ActivityManager am = (ActivityManager) context.getSystemService(Context.ACTIVITY_SERVICE);
        if(Build.VERSION.SDK_INT>Build.VERSION_CODES.KITKAT){
            List<ActivityManager.RunningAppProcessInfo> runningAppProcesses = am.getRunningAppProcesses();
            for(ActivityManager.RunningAppProcessInfo processInfo : runningAppProcesses){
                if (processInfo.importance == ActivityManager.RunningAppProcessInfo.IMPORTANCE_FOREGROUND){
                    for(String activeProcess : processInfo.pkgList){
                        if(activeProcess.equals(context.getPackageName()))
                            isInBackground=false;
                    }
                }
            }
        }else{
            List<ActivityManager.RunningTaskInfo> taskInfo = am.getRunningTasks(1);
            ComponentName componentInfo = taskInfo.get(0).topActivity;
            if (componentInfo.getPackageName().equals(context.getPackageName())) {
                isInBackground = false;
            }
        }
        return isInBackground;
    }

    //clears notification tray

    public static void clearNotification(Context context){
        NotificationManager notificationManager = (NotificationManager)context.getSystemService(Context.NOTIFICATION_SERVICE);
        notificationManager.cancelAll();
    }

}
