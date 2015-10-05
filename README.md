# NTCIR11 Workspace

## 概要
TF-IDF特徴量からNTCIR11のタスクを実行
MAPを計算


## 導入テスト
```
git clone https://github.com/ragiko/ntcir11.git
cd ntcir11/
git submodule init
git submodule update
rake p=query_likelihood_t_slide init
rake p=query_likelihood_t_slide all
```

# ワークフロー
1. workspace/にprojectを作成
2. main.pyにresult/に結果を格納するコードを作成
3. rake p=project_name all でmap値を計算

## MAP計算
``` 
# tfidfのプロジェクトに対して実行
rake p=tfidf all
rake p=tfidf all_soft # キャッシュファイルを消さない
```

## 注意
- ワークスペースを利用する時(rake p=query_likelihood_t_slide allなど)を利用する前は必ずrake initすること(rake p=query_likelihood_t_slide init)のように
