# シンプルUNOゲーム Simple UNO
## 説明
これはコマンドプロンプトでUNOを遊ぶゲームです。

This program is UNO game in command prompt.


pythonがあれば遊ぶことができます。

You can play with python.

## 遊び方
pythonをインストールしたPCでコマンドプロンプトを立ち上げます。

Install python and launch the command prompt.


ファイルのある場所に移動し、以下コマンドを実行します。

Type this command.

""" >python main.py """

（uvの練習用にuvで作成しましたが、パッケージを使いませんでした。）

---
MEMO
uvで作成
uv init project -p * で　*バージョンのpythonを指定する。
uv python list で使用可能pythonの確認
uv add ***	プロジェクトに依存関係を追加
uv remove ***	プロジェクトから依存関係を削除
uv run **.py	uvでpythonスクリプト(.py)を実行する
uv pip install ***	uvでpipコマンドを実行する
uv self update	uvを最新バージョンにする
