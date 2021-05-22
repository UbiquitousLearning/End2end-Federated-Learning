package com.example;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Context;
import android.os.Bundle;

import com.demo.R;
import com.example.websocket.service.MnnTrainService;

public class MainActivity_test extends AppCompatActivity {

    MnnTrainService mnnTrainService = new MnnTrainService();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mnnTrainService.onCreate();

    }


}