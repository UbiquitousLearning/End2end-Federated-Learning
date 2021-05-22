package com.example.websocket.service;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;

import com.example.nativemnn.mnn.MNNDataNative;
import static com.example.websocket.constants.Constants.TRAIN_DATA_FILE_PATH;
import static com.example.websocket.constants.Constants.TRAIN_MODEL_FILE_PATH;

public class MnnTrainService extends Service {
    private MNNDataNative mnnDataNative;

    public MnnTrainService(){

    }

    @Override
    public void onCreate() {
        super.onCreate();

        mnnTrainNative();

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

    public void mnnTrainNative(){
        String result = mnnDataNative.nativeCreateDatasetFromFile(TRAIN_MODEL_FILE_PATH,TRAIN_DATA_FILE_PATH);
    }
}
