package com.demo;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.fragment.app.Fragment;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link MnnTrainFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class MnnTrainFragment extends Fragment {

    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "param1";
    private static final String ARG_PARAM2 = "param2";

    // TODO: Rename and change types of parameters
    private String mParam1;
    private String mParam2;
    private String trainInfo;

    private TextView stateText;

    public MnnTrainFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param param1 Parameter 1.
     * @param param2 Parameter 2.
     * @return A new instance of fragment MnnTrainFragment.
     */
    // TODO: Rename and change types and number of parameters
    public static MnnTrainFragment newInstance(String param1, String param2) {
        MnnTrainFragment fragment = new MnnTrainFragment();
        Bundle args = new Bundle();
        args.putString(ARG_PARAM1, param1);
        args.putString(ARG_PARAM2, param2);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            mParam1 = getArguments().getString(ARG_PARAM1);
            mParam2 = getArguments().getString(ARG_PARAM2);
        }

        //开启线程，动态展示设备状态

//        new Thread(new Runnable() {
//            @Override
//            public void run() {
//                try {
//                    //需要在子线程中处理的逻辑
//                    stateText.setText(trainInfo);
//                    Thread.sleep(100);
//                } catch (InterruptedException e) {
//                    e.printStackTrace();
//                }
//
//            }
//        }).start();

    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment



        return inflater.inflate(R.layout.fragment_mnn_train, container, false);
    }


//    @Override
//    public void onAttach(Activity activity) {
//        super.onAttach(activity);
//        trainInfo = ((MainActivity) activity).getTrainInfo();//通过强转成宿主activity，就可以获取到传递过来的数据
//    }

}