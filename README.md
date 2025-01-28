uvで作成
uv init project -p * で　*バージョンのpythonを指定する。
uv python list で使用可能pythonの確認
uv add ***	プロジェクトに依存関係を追加
uv remove ***	プロジェクトから依存関係を削除
uv run **.py	uvでpythonスクリプト(.py)を実行する
uv pip install ***	uvでpipコマンドを実行する
uv self update	uvを最新バージョンにする