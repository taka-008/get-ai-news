#!/bin/bash
echo "AI News Dashboard セットアップ"
echo ""

# Pythonの確認
if ! command -v python3 &> /dev/null; then
    echo "[エラー] Python3がインストールされていません。"
    exit 1
fi

# 仮想環境の作成
echo "仮想環境を作成中..."
python3 -m venv venv
source venv/bin/activate

# パッケージのインストール
echo "パッケージをインストール中..."
pip install -r requirements.txt

# .envファイルの作成
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "[重要] .envファイルにANTHROPIC_API_KEYを設定してください。"
fi

echo ""
echo "セットアップ完了！"
echo "bash start.sh を実行してアプリを起動できます。"
