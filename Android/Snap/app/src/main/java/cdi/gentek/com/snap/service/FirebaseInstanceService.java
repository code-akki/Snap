package cdi.gentek.com.snap.service;

import android.content.Intent;
import android.content.SharedPreferences;
import android.support.v4.content.LocalBroadcastManager;
import android.util.Log;

import com.google.firebase.iid.FirebaseInstanceId;
import com.google.firebase.iid.FirebaseInstanceIdService;

import cdi.gentek.com.snap.app.Config;

/**
 * Created by apple on 10/03/18.
 */

public class FirebaseInstanceService extends FirebaseInstanceIdService{
    private static final String TAG = FirebaseInstanceIdService.class.getSimpleName();

    @Override
    public void onTokenRefresh() {
        super.onTokenRefresh();

        String refreshedToken = FirebaseInstanceId.getInstance().getToken();
        Log.d(TAG,refreshedToken);

        //save it in saved preference
        SharedPreferences sharedPreferences = getApplicationContext().getSharedPreferences(Config.SHARED_PREF,0);
        SharedPreferences.Editor editor = sharedPreferences.edit();
        editor.putString("regId",refreshedToken);
        editor.commit();
        //store it in Firebase

        //Notify UI showing the registration is complete
        Intent intent = new Intent(Config.REGISTRATION_COMPLETE);
        intent.putExtra("token", refreshedToken);
        LocalBroadcastManager.getInstance(this).sendBroadcast(intent);

    }
}
