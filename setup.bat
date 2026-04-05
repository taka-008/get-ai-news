@echo off
echo AI News Dashboard セットアップ
echo.

REM Pythonの確認
python --version >nul 2>&1
if errorlevel 1 (
    echo [エラー] Pythonがインストールされていません。
    pause
    exit /b 1
)

REM 仮想環境の作成
echo 仮想環境を作成中...
python -m venv venv
call venv\Scripts\activate.bat

REM パッケージのインストール
echo パッケージをインストール中...
pip install -r requirements.txt

REM .envファイルの作成
if not exist .env (
    copy .env.example .env
    echo.
    echo [重要] .envファイルにANTHROPIC_API_KEYを設定してください。
)

echo.
echo セットアップ完了！
echo start.batを実行してアプリを起動できます。
pause
