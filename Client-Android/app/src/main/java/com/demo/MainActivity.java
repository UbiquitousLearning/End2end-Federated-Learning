package com.demo;

import android.Manifest;
import android.annotation.SuppressLint;
import android.content.Context;
import android.content.pm.PackageManager;
import android.net.wifi.WifiInfo;
import android.net.wifi.WifiManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.text.TextUtils;
import android.util.Log;
import android.view.View;
import android.widget.ScrollView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;
import androidx.databinding.DataBindingUtil;

import com.demo.databinding.ActivityMainBinding;

import com.example.nativemnn.mnn.MNNDataNative;

import org.jetbrains.annotations.NotNull;
import org.json.JSONObject;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.Base64;

import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import okhttp3.WebSocket;
import okhttp3.WebSocketListener;
import okio.ByteString;


public class MainActivity extends AppCompatActivity {

    public static final String TAG = "websocketclient";
    public static final String SERVER_URL = "ws://10.128.207.225:8080/ws";
    //public static final String dir = Environment.getExternalStorageDirectory().toString();
    //public static final String TRAIN_MODEL_FILE_PATH = dir+"/mnn_data/mnist.snapshot.mnn";
    public static final String TRAIN_MODEL_FILE_PATH = "/data/local/tmp/mnn/mnist.snapshot.mnn";
    public static final String TRAIN_DATA_FILE_PATH = "/data/local/tmp/mnist_data";

    private OkHttpClient mOkHttpClient;
    private WebSocket mWebSocket;
    private TextView trainStateText;
    private TextView deviceStateText;
    private TextView trainTimeText;
    private TextView downLoadTimeText;
    private TextView trainTimeLastRoundText;
    private TextView localTrainInfoText;
    private ActivityMainBinding binding;
    private String trainInfo;
    private int deviceState;
    private String deviceLocalIp;
    private String localEpochs;
    private String batchSize;
    private String learningRate;
    private Long trainTimeLastRound;
    private Long downLoadTime;

    public MNNDataNative mnnDataNative;

    private Handler mWebSocketHandler = new Handler(new Handler.Callback() {
        @Override
        public boolean handleMessage(@NonNull Message msg) {
            appendMsgDisplay((String) msg.obj);
            return false;
        }
    });


    private Handler trainTextHandler = new Handler(new Handler.Callback() {
        @SuppressLint("SetTextI18n")
        @Override
        public boolean handleMessage(@NotNull Message msg) {
            if(msg.what == 1) trainStateText.setText(trainInfo);
            if(msg.what == 2) trainStateText.setText("Not Training");
            return false;
        }
    });

    private Handler deviceTextHandler = new Handler(new Handler.Callback() {
        @SuppressLint("SetTextI18n")
        @Override
        public boolean handleMessage(@NotNull Message msg) {
            if(msg.what == 0) deviceStateText.setText("WELCOME");
            if(msg.what == 1) deviceStateText.setText("OPEN CONNECTION");
            if(msg.what == 2) deviceStateText.setText("JOIN SYSTEM");
            if(msg.what == 3) deviceStateText.setText("UPLOADING DATA");
            if(msg.what == 4) deviceStateText.setText("WAITING TO DOWNLOAD DATA");
            if(msg.what == 5) deviceStateText.setText("TRAIN");
            if(msg.what == -1) deviceStateText.setText("LEAVE THE SYSTEM");
            return false;
        }
    });

    private Handler localTrainInfoTextHandler = new Handler(new Handler.Callback() {
        @SuppressLint("SetTextI18n")
        @Override
        public boolean handleMessage(@NotNull Message msg) {
            if(msg.what == 1)
                localTrainInfoText.setText(
                    "localEpochs:"+localEpochs+"\nbatchSize:"+batchSize+"\nlearningRate:"+learningRate);
            return false;
        }
    });


    private static final int REQUEST_EXTERNAL_STORAGE = 1;
    private static String[] PERMISSIONS_STORAGE = {
            Manifest.permission.READ_EXTERNAL_STORAGE,
            Manifest.permission.WRITE_EXTERNAL_STORAGE };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = DataBindingUtil.setContentView(this, R.layout.activity_main);

        trainStateText=(TextView)findViewById(R.id.train_state);
        deviceStateText=(TextView)findViewById(R.id.device_state);
        localTrainInfoText=(TextView)findViewById(R.id.local_train_info);
        trainTimeText=(TextView)findViewById(R.id.textView16);
        downLoadTimeText=(TextView)findViewById(R.id.textView17);
        trainTimeLastRoundText=(TextView)findViewById(R.id.textView18);
//        stateText.setText("ready for connection");

        deviceState = 0;
        trainTimeLastRound = 0L;
        deviceLocalIp = getIpFromWifi();
        Log.d(TAG,"deviceLocalIp:"+deviceLocalIp);
        Message msg = new Message();
        msg.what=0;
        deviceTextHandler.sendMessage(msg);

        new Thread(new Runnable() {
            @SuppressLint("SetTextI18n")
            @Override
            public void run() {
                try{
                    //需要在子线程中处理的逻辑
                    while (true){
                        //
                        Message msg1 = new Message();
                        msg1.what = 1;
                        localTrainInfoTextHandler.sendMessage(msg1);

                        Message msg = new Message();
                        if(deviceState == 5) {
                            String epochAndLoss = mnnDataNative.getEpochAndLoss();
                            String epoch = epochAndLoss.split(",")[0];
                            String loss = epochAndLoss.split(",")[1];
                            trainInfo = "Training:"+epoch+"/"+localEpochs+"\nCurrent Loss:"+loss;
                            msg.what = 1;
                            trainTextHandler.sendMessage(msg);
                        }
                        else {
                            msg.what = 2;
                            trainTextHandler.sendMessage(msg);
                        }
                        Thread.sleep(100);
                    }
                } catch (InterruptedException e) {
                    Log.e(TAG,"onCreate:"+e.toString());
                    e.printStackTrace();
                }

            }
        }).start();


        //动态获取文件读取权限
        if (Build.VERSION.SDK_INT >= 23) {
            //验证是否许可权限
            for (String str : PERMISSIONS_STORAGE) {
                if (this.checkSelfPermission(str) != PackageManager.PERMISSION_GRANTED) {
                    //申请权限
                    this.requestPermissions(PERMISSIONS_STORAGE, REQUEST_EXTERNAL_STORAGE);
                }
            }
        }
    }

    @Override
    protected void onStart() {
        super.onStart();
        //NetWorkMonitorManager.getInstance().register(this);
    }

    @Override
    protected void onStop() {
        super.onStop();
        //NetWorkMonitorManager.getInstance().unregister(this);

    }

    private void webSocketConnect() {
        mOkHttpClient = new OkHttpClient();
        Request request = new Request.Builder()
                .url(SERVER_URL)
                .build();
        ClientWebSocketListener listener=new ClientWebSocketListener();
        mOkHttpClient.newWebSocket(request,listener);
        mOkHttpClient.dispatcher().executorService().shutdown();
    }


    public void connect(View view) {
        webSocketConnect();
        Message msg = new Message();
        deviceState = 1;//连接
        msg.what = 1;
        deviceTextHandler.sendMessage(msg);
    }

    public void sendMsg(View view) {
        Message msg = new Message();
        deviceState = 2;//加入系统
        msg.what = 2;
        deviceTextHandler.sendMessage(msg);

        mWebSocket.send("hello");
        //处理完成后给handler发送消息

        /*
        if (mWebSocket!=null){
            //输入框信息
            if (binding.inputMsg.getText()!=null){
                String text = binding.inputMsg.getText().toString();
                mWebSocket.send(text);
            }
        }else {
            appendMsgDisplay("no connection");
        }

         */
    }

    @RequiresApi(api = Build.VERSION_CODES.O)
    public void sendMnnModel(float loss,int trainSamples,float acc,int testSamples,long trainTime,long uploadTimestamp) throws Exception {

        deviceState = 3;//发送数据，上传状态
        Message msg = new Message();
        msg.what = 3;
        deviceTextHandler.sendMessage(msg);

        if(mWebSocket!=null){
            //从存储中读取mnn
            byte[] data = new byte[0];
            data = getContent(TRAIN_MODEL_FILE_PATH);

            Log.d(TAG,"data size:"+data.length);
            byte[] data_length = intToByteArray(data.length);

            //
            JSONObject obj = new JSONObject();
            obj.put("loss",loss);
            obj.put("train_samples", trainSamples);
            obj.put("acc",acc);
            obj.put("test_samples",testSamples);
            obj.put("train_time",trainTime);
            obj.put("upload_timestamp",uploadTimestamp);
            obj.put("model", Base64.getEncoder().encodeToString(data));

            byte[] datajson = obj.toString().getBytes(StandardCharsets.UTF_8);

            //发送mnn model
            ByteString data_bytestring = ByteString.of(datajson,0,datajson.length);

            mWebSocket.send(data_bytestring);

            Log.d(TAG,"send over");
        }
        else{
            appendMsgDisplay("no connection");
        }
    }

    public void close(View view) {
        if(null!=mWebSocket){
            mWebSocket.close(1000,"client say bye");
            //处理完成后给handler发送消息
            Message msg = new Message();
            deviceState = -1;//断连
            msg.what = -1;
            deviceTextHandler.sendMessage(msg);
            mWebSocket=null;
        }
    }

    public void clear(View view) {
        binding.tvMsg.setText("");
    }

    private final class ClientWebSocketListener extends WebSocketListener {
        @Override
        public void onOpen(@NotNull WebSocket webSocket, @NotNull Response response) {
            mWebSocket=webSocket;
            showServerMsg("connected");
//            //处理完成后给handler发送消息
//            Message msg = new Message();
//            msg.what = 1;
//            textHandler.sendMessage(msg);
        }

        @RequiresApi(api = Build.VERSION_CODES.O)
        @Override
        public void onMessage (@NotNull WebSocket webSocket, @NotNull String text) {
            try{
                Log.d(TAG,"received text, chosen");
                Log.d(TAG, String.valueOf(text.length()));

                //json处理
                JSONObject jsonObject = new JSONObject(text);
                String taskKind = jsonObject.get("kind").toString();
                //String chosenIp = jsonObject.get("chosenIp").toString();
                String downloadTimestamp = jsonObject.get("downloadTimestamp").toString();

                long curTimestamp = LocalDateTime.now().toInstant(ZoneOffset.of("+8")).toEpochMilli();

                downLoadTime = curTimestamp - Long.parseLong(downloadTimestamp);

                //localEpochs batchSize learningRate
                localEpochs = jsonObject.get("localEpochs").toString();
                batchSize  = jsonObject.get("batchSize").toString();
                learningRate = jsonObject.get("learningRate").toString();


                //初始化init模型存储到本地
                if(taskKind.equals("send_task")){

                    //save init model
                    showServerMsg("receive init model from server");
                    byte [] byteArray = Base64.getDecoder().decode(jsonObject.get("model").toString());
                    saveFile(TRAIN_MODEL_FILE_PATH,byteArray);


                }
                else{
                    //save aggregated model
                    showServerMsg("receive aggregate model from server");
                    byte [] byteArray = Base64.getDecoder().decode(jsonObject.get("model").toString());
                    saveFile(TRAIN_MODEL_FILE_PATH,byteArray);

                }


                //train
                Log.d(TAG,TRAIN_MODEL_FILE_PATH);
                Message msg = new Message();
                deviceState = 5;//训练状态
                msg.what = 5;
                deviceTextHandler.sendMessage(msg);

                long startTrainTime = LocalDateTime.now().toInstant(ZoneOffset.of("+8")).toEpochMilli();
                final String result = mnnDataNative.nativeCreateDatasetFromFile(TRAIN_MODEL_FILE_PATH,TRAIN_DATA_FILE_PATH);
                long endTrainTime = LocalDateTime.now().toInstant(ZoneOffset.of("+8")).toEpochMilli();
                long trainTime=endTrainTime-startTrainTime;

                //show train massage
                String[] res = result.split(",");
                showServerMsg("loss,trainSamples,acc,testSamples:"+
                        res[0]+" "+
                        res[1]+" "+
                        res[2]+" "+
                        res[3]);
                showServerMsg("train finished");

                trainTimeText.setText(String.valueOf(trainTime)+"ms");
                downLoadTimeText.setText(String.valueOf(downLoadTime)+"ms");
                trainTimeLastRoundText.setText(String.valueOf(trainTimeLastRound)+"ms");
                trainTimeLastRound = trainTime;

                long uploadTimestamp = LocalDateTime.now().toInstant(ZoneOffset.of("+8")).toEpochMilli();

                sendMnnModel(Float.parseFloat(res[0]),
                        Integer.parseInt(res[1]),
                        Float.parseFloat(res[2]),
                        Integer.parseInt(res[3]),
                        trainTime,
                        uploadTimestamp
                );

                deviceState = 4;//等待下载数据
                Message msg2 = new Message();
                msg2.what = 4;
                deviceTextHandler.sendMessage(msg2);


            }
            catch (Exception e) {
                Log.e(TAG,"onMessage:"+e.toString());
            }
        }

        @Override
        public void onMessage(@NotNull WebSocket webSocket, ByteString bytes) {
            Log.d(TAG,"received bytes");
            showServerMsg(bytes.utf8());
        }

        @Override
        public void onClosing(@NotNull WebSocket webSocket, int code, @NotNull String reason) {
            if(null!=mWebSocket){
                mWebSocket.close(1000,"close");
                mWebSocket=null;
            }
        }

        @Override
        public void onClosed(@NotNull WebSocket webSocket, int code, @NotNull String reason) {
            Message message= Message.obtain();
            message.obj=reason;
            message.what = 2;
            mWebSocketHandler.sendMessage(message);
        }

        @Override
        public void onFailure(@NotNull WebSocket webSocket, @NotNull Throwable t, @Nullable Response response) {
            Message message= Message.obtain();
            message.obj= t.getLocalizedMessage();
            message.what = 3;
            mWebSocketHandler.sendMessage(message);
        }
    }

    private void showServerMsg(String msg){
        Message message= Message.obtain();
        message.obj="$ "+msg;
        message.what = 1;
        mWebSocketHandler.sendMessage(message);
    }

    private void appendMsgDisplay(String msg) {
        Log.d(TAG,"msg :"+ msg);
        StringBuilder textBuilder = new StringBuilder();
        if (!TextUtils.isEmpty(binding.tvMsg.getText())) {
            textBuilder.append(binding.tvMsg.getText().toString());
            textBuilder.append("\n");
        }
        textBuilder.append(msg);
        textBuilder.append("\n");
        binding.tvMsg.setText(textBuilder.toString());
        binding.tvMsg.post(new Runnable() {
            @Override
            public void run() {
                binding.scrollView.fullScroll(ScrollView.FOCUS_DOWN);
            }
        });
    }



    public String getIpFromWifi() {
        //获取wifi服务
        WifiManager wifiManager = (WifiManager) getApplicationContext().getSystemService(Context.WIFI_SERVICE);
        //判断wifi是否开启
        if (!wifiManager.isWifiEnabled()) {
            wifiManager.setWifiEnabled(true);
        }
        WifiInfo wifiInfo = wifiManager.getConnectionInfo();
        int ipAddress = wifiInfo.getIpAddress();
        String ip = intToIp(ipAddress);
        return ip;
    }

    //获取Wifi ip 地址
    private String intToIp(int i) {
        return (i & 0xFF) + "." +
                ((i >> 8) & 0xFF) + "." +
                ((i >> 16) & 0xFF) + "." +
                (i >> 24 & 0xFF);
    }

    public static byte[] getContent(String filePath) throws IOException {
        File file = new File(filePath);

        long fileSize = file.length();
        if (fileSize > Integer.MAX_VALUE) {
            Log.d(TAG,"file too big...");
            return null;
        }

        FileInputStream fi = new FileInputStream(file);
        byte[] buffer = new byte[(int) fileSize];
        int offset = 0;
        int numRead = 0;

        while (offset < buffer.length
                && (numRead = fi.read(buffer, offset, buffer.length - offset)) >= 0) {
            offset += numRead;
        }

        // 确保所有数据均被读取
        if (offset != buffer.length) {
            throw new IOException("Could not completely read file "
                    + file.getName());
        }
        fi.close();
        return buffer;
    }

    public static void saveFile(String path, byte[] data)throws Exception {
        if(data != null){
            Log.d(TAG,"save file");
            FileOutputStream out = new FileOutputStream(path);//指定写到哪个路径中
            FileChannel fileChannel = out.getChannel();
            fileChannel.write(ByteBuffer.wrap(data)); //将字节流写入文件中
            fileChannel.force(true);//强制刷新
            fileChannel.close();

        }
    }



    //byte 数组与 int 的相互转换
    public static int byteArrayToInt(byte[] b) {
        return   b[3] & 0xFF |
                (b[2] & 0xFF) << 8 |
                (b[1] & 0xFF) << 16 |
                (b[0] & 0xFF) << 24;
    }

    public static byte[] intToByteArray(int a) {
        return new byte[] {
                (byte) ((a >> 24) & 0xFF),
                (byte) ((a >> 16) & 0xFF),
                (byte) ((a >> 8) & 0xFF),
                (byte) (a & 0xFF)
        };
    }
}
