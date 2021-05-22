package com.example.websocket.client;

import android.util.Log;

import androidx.annotation.Nullable;

import org.jetbrains.annotations.NotNull;

import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import okhttp3.WebSocket;
import okhttp3.WebSocketListener;
import okio.ByteString;

class ClientWebSocketListener extends WebSocketListener {

    @Override
    public void onOpen(@NotNull WebSocket webSocket, @NotNull Response response){

    }

    @Override
    public void onClosing(@NotNull WebSocket webSocket, int code, @NotNull String reason){

    }

    @Override
    public void onClosed(@NotNull WebSocket webSocket, int code, @NotNull String reason) {

    }


    @Override
    public void onMessage (@NotNull WebSocket webSocket, @NotNull String text){

    }

    @Override
    public void onMessage(@NotNull WebSocket webSocket, ByteString bytes) {

    }

    @Override
    public void onFailure(@NotNull WebSocket webSocket, @NotNull Throwable t, @Nullable Response response) {

    }



}
