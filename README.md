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

## 導入テスト補足
- ~/.bashrcとかにPYTHONPATHを設定 (hymlabモジュールを呼び出すため)
  - export PYTHONPATH=(自分のcloneしたntcir11のpath)/lib:$PYTHONPATH
    - 例) export PYTHONPATH=~/programing/ntcir11/lib:$PYTHONPATH
- 依存モジュール
  - sudo pip install nkf
  - sudo gem install systemu

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

## エラーについて
### error1
- Q

```
➜  ntcir11 git:(master) git submodule update
Cloning into 'lib/hymlab'...
remote: Counting objects: 181, done.
remote: Total 181 (delta 0), reused 0 (delta 0), pack-reused 181
Receiving objects: 100% (181/181), 33.24 KiB, done.
Resolving deltas: 100% (109/109), done.
Submodule path 'lib/hymlab': checked out '54a676929b5e77b0191248001109b8c0769ee9f3'
No submodule mapping found in .gitmodules for path 'workspace/sentence2vec/sentence2vec_core'
```

- A

```
git rm --cached workspace/sentence2vec/sentence2vec_core
```

### error2
- Q

```
sudo gem install systemuで opensslが...
Unable to require openssl, install OpenSSL and rebuild ruby (preferred) or use non-HTTPS source
```

- A

```
gem source -r https://rubygems.org/
gem source -a http://rubygems.org/
```

### error3
- Q

```
$Error: Traceback (most recent call last):
  File "./workspace/query_likelihood_t_slide/main.py", line 5, in <module>
    import hymlab.text as ht
  File "/home/seko/ntcir11/lib/hymlab/text/__init__.py", line 7, in <module>
    from .text import *
  File "/home/seko/ntcir11/lib/hymlab/text/text.py", line 6, in <module>
    from hymlab.text.util import *
  File "/home/seko/ntcir11/lib/hymlab/text/util.py", line 4, in <module>
    import nkf
ImportError: No module named nkf

ERROR: workspace results is not exist
```

- A

```
sudo pip install nkf
```

