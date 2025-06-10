package com.alibaba.example.baseknowledge.token;

import com.hankcs.hanlp.HanLP;
import com.hankcs.hanlp.corpus.tag.Nature;
import com.hankcs.hanlp.seg.common.Term;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * @Author 灵盛
 * @create 2025/6/8 18:41
 * 余弦相似度原理：https://alidocs.dingtalk.com/i/nodes/gvNG4YZ7JneLapPoi2PbdPj4V2LD0oRE
 */
public class cosineSimilarity {
    public static void main(String[] args) {
        String text1 = "老板，您的实名认证任务还在**审核中**，因此暂时无法修改许可证。请您耐心等待实名认证审核通过后，再进行许可证的修改。感谢您的理解和配合！";
        String text2 = "老板，您好！当前您的**实名认证任务**还在审核中，同时**店铺信息审核任务**的状态是材料收集未完成。在这个阶段，您**不需要修改许可证**。请先完成当前的任务，如有其他疑问，随时欢迎向我咨询。";

        // 从文本中提取出关键词数组
        List<String> wordListA = extractWordFromText(text1);
        List<String> wordListB = extractWordFromText(text2);
        System.out.println("关键词1: " + wordListA);
        System.out.println("关键词1: " + wordListB);
        List<Double> vectorA = new ArrayList<>();
        List<Double> vectorB = new ArrayList<>();

        // 将关键词数组转换为词向量并保存在 vectorA 和 vectorB 中
        convertWordList2Vector(wordListA,wordListB,vectorA,vectorB);

        // 计算向量夹角的余弦值
        double cosine = Double.parseDouble(String.format("%.4f",countCosine(vectorA,vectorB)));
        System.out.println(cosine);

    }


    // 提取文本中有实意的词
    public static List<String> extractWordFromText(String text){
        // resultList 用于保存提取后的结果
        List<String> resultList = new ArrayList<>();

        // 当 text 为空字符串时，使用分词函数会报错，所以需要提前处理这种情况
        if(text.length() == 0){
            return resultList;
        }

        // 分词
        List<Term> termList = HanLP.segment(text);
        // 提取所有的 1.名词/n ; 2.动词/v ; 3.形容词/a
        for (Term term : termList) {
            if(term.nature == Nature.n || term.nature == Nature.v || term.nature == Nature.a
                    || term.nature == Nature.vn || term.nature == Nature.m || term.nature == Nature.q){
                resultList.add(term.word);
            }
        }
        // 如果分词为空，则返回他本身
        if (resultList.isEmpty()){
            resultList.add(text);
        }
        return resultList;
    }

    /**
     * @Description : 将单词数组转换为单词向量，结果保存在 vectorA 和 vectorB 里
     * @param wordListA : 文本 A 的单词数组
     * @param wordListB : 文本 B 的单词数组
     * @param vectorA   : 文本 A 转换成为的向量 A
     * @param vectorB   : 文本 B 转换成为的向量 B
     * @return vocabulary : 词汇表
     */
    private static List<String> convertWordList2Vector(List<String> wordListA, List<String> wordListB, List<Double> vectorA, List<Double> vectorB){
        // 词汇表
        List<String> vocabulary = new ArrayList<>();

        // 获取词汇表 wordListA 的频率表，并同时建立词汇表
        Map<String,Double> frequencyTableA = buildFrequencyTable(wordListA, vocabulary);

        // 获取词汇表 wordListB 的频率表，并同时建立词汇表
        Map<String,Double> frequencyTableB = buildFrequencyTable(wordListB, vocabulary);
        System.out.println("词频表1: " + frequencyTableA);
        System.out.println("词频表2: " + frequencyTableB);

        // 根据频率表得到向量
        getWordVectorFromFrequencyTable(frequencyTableA,vectorA,vocabulary);
        getWordVectorFromFrequencyTable(frequencyTableB,vectorB,vocabulary);
        System.out.println("词频向量表1: " + vectorA);
        System.out.println("词频向量表2: " + vectorB);

        return vocabulary;
    }

    /**
     * @param wordList：单词数组
     * @param vocabulary: 词汇表
     * @return Map<String,Double>: key为单词，value为频率
     * @Description 建立词汇表 wordList 的频率表，并同时建立词汇表
     */
    private static Map<String,Double> buildFrequencyTable(List<String> wordList, List<String> vocabulary){
        // 先建立频数表
        Map<String,Integer> countTable = new HashMap<>();
        for (String word : wordList) {
            if(countTable.containsKey(word)){
                countTable.put(word,countTable.get(word)+1);
            }
            else{
                countTable.put(word,1);
            }
            // 词汇表中是无重复元素的，所以只在 vocabulary 中没有该元素时才加入
            if(!vocabulary.contains(word)){
                vocabulary.add(word);
            }
        }
        // totalCount 用于记录词出现的总次数
        int totalCount = wordList.size();
        // 将频数表转换为频率表
        Map<String,Double> frequencyTable = new HashMap<>();
        for (String key : countTable.keySet()) {
            frequencyTable.put(key,(double)countTable.get(key)/totalCount);
        }
        return frequencyTable;
    }

    /**
     * @param frequencyTable : 频率表
     * @param wordVector     : 转换后的词向量
     * @param vocabulary     : 词汇表
     * @Description 根据词汇表和文本的频率表计算词向量，最后 wordVector 和 vocabulary 应该是同维的
     */
    private static void getWordVectorFromFrequencyTable(Map<String, Double> frequencyTable, List<Double> wordVector, List<String> vocabulary){
        for (String word : vocabulary) {
            double value = 0.0;
            if(frequencyTable.containsKey(word)){
                value = frequencyTable.get(word);
            }
            wordVector.add(value);
        }
    }

    /**
     * @Description 计算向量 A 和向量 B 的夹角余弦值
     * @param vectorA   : 词向量 A
     * @param vectorB   : 词向量 B
     * @return
     */
    private static double countCosine(List<Double> vectorA, List<Double> vectorB){
        // 分别计算向量的平方和
        double sqrtA = countSquareSum(vectorA);
        double sqrtB = countSquareSum(vectorB);

        // 计算向量的点积
        double dotProductResult = 0.0;
        for(int i = 0;i < vectorA.size();i++){
            dotProductResult += vectorA.get(i) * vectorB.get(i);
        }

        return dotProductResult/(sqrtA*sqrtB);
    }

    // 计算向量平方和的开方
    private static double countSquareSum(List<Double> vector){
        double result = 0.0;
        for (Double value : vector) {
            result += value*value;
        }
        return Math.sqrt(result);
    }
}


