package com.alibaba.example.baseknowledge.token;

import com.alibaba.fastjson.JSONObject;
import com.hankcs.hanlp.HanLP;
import com.hankcs.hanlp.corpus.tag.Nature;
import com.hankcs.hanlp.seg.common.Term;

import java.util.List;

/**
 * @Author 灵盛
 * @create 2025/6/8 18:38
 */
public class tokenization {

    public static void main(String[] args) {
        // 分词
        String text = "智能城策异常数据检测";
        List<Term> termList = HanLP.segment(text);
        System.out.println(JSONObject.toJSONString(termList));
        // 提取所有的 1.名词/n ; 2.动词/v ; 3.形容词/a
        for (Term term : termList) {
            if(term.nature == Nature.n || term.nature == Nature.v || term.nature == Nature.a
                    || term.nature == Nature.vn || term.nature == Nature.m || term.nature == Nature.q){
                System.out.println(term.word);
            }
        }
    }
}
