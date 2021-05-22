package com.example.websocket.service;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;


public class ClientWebSocketService extends Service {

    /** 绑定的客户端接口 */

    public ClientWebSocketService(){

    }

    @Override
    public void onCreate() {
        super.onCreate();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        return super.onStartCommand(intent, flags, startId);
    }


    @Override
    public void onDestroy() {

    }

    @Override
    public IBinder onBind(Intent intent) {
        // TODO: Return the communication channel to the service.
        throw new UnsupportedOperationException("Not yet implemented");
    }




}
