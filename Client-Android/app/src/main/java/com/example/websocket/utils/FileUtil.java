package com.example.websocket.utils;

import android.util.Log;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;

import static com.example.websocket.constants.Constants.TAG;

public class FileUtil {

    public static byte[] getFileContent(String filePath) throws IOException {
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

    public static void saveFileToPath(String path, byte[] data)throws Exception {
        if(data != null){
            Log.d(TAG,"save file to path:"+path);
            FileOutputStream out = new FileOutputStream(path);//指定写到哪个路径中
            FileChannel fileChannel = out.getChannel();
            fileChannel.write(ByteBuffer.wrap(data)); //将字节流写入文件中
            fileChannel.force(true);//强制刷新
            fileChannel.close();
        }
    }

}
