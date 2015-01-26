# NTCIR11 Workspace

## 概要
TF-IDF特徴量からNTCIR11のタスクを実行
MAPを計算

## 導入
```
rake init

# or

mkdir ./workspace/result
mkdir ./workspace/tmp
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

