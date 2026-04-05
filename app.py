"""
AI News Dashboard
メインFlaskアプリケーション
"""
import os
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/")
def index():
    """トップページ：本日のAIニュース ランキング"""
    return render_template("index.html", companies=_get_companies())


@app.route("/company/<company_key>")
def company_page(company_key):
    """企業別ページ"""
    from news_sources import COMPANY_FEEDS
    if company_key not in COMPANY_FEEDS:
        return render_template("404.html"), 404
    company = COMPANY_FEEDS[company_key]
    return render_template(
        "company.html",
        company_key=company_key,
        company=company,
        companies=_get_companies(),
    )


@app.route("/api/news/general")
def api_general_news():
    """一般AIニュースAPIエンドポイント"""
    try:
        from news_fetcher import fetch_general_news
        from news_processor import process_news_with_claude

        articles = fetch_general_news()
        result = process_news_with_claude(articles, context="general")
        return jsonify({"success": True, "data": result})
    except Exception as e:
        logger.error(f"General news API error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/news/company/<company_key>")
def api_company_news(company_key):
    """企業別ニュースAPIエンドポイント"""
    from news_sources import COMPANY_FEEDS
    if company_key not in COMPANY_FEEDS:
        return jsonify({"success": False, "error": "Company not found"}), 404

    try:
        from news_fetcher import fetch_company_news
        from news_processor import process_news_with_claude

        company = COMPANY_FEEDS[company_key]
        articles = fetch_company_news(company_key)
        result = process_news_with_claude(
            articles, context=company["display_name"]
        )
        return jsonify({"success": True, "data": result, "company": company})
    except Exception as e:
        logger.error(f"Company news API error ({company_key}): {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/refresh/<target>")
def api_refresh(target):
    """キャッシュをクリアして再取得"""
    import glob
    cache_dir = os.path.join(os.path.dirname(__file__), "cache")

    try:
        if target == "all":
            for f in glob.glob(os.path.join(cache_dir, "*.json")):
                os.remove(f)
        elif target == "general":
            for f in glob.glob(os.path.join(cache_dir, "general_*.json")):
                os.remove(f)
            for f in glob.glob(os.path.join(cache_dir, "processed_general_*.json")):
                os.remove(f)
        else:
            for f in glob.glob(os.path.join(cache_dir, f"*{target}*.json")):
                os.remove(f)
        return jsonify({"success": True, "message": f"Cache cleared for: {target}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def _get_companies():
    from news_sources import COMPANY_FEEDS
    return {k: {"display_name": v["display_name"], "color": v["color"], "icon": v["icon"]}
            for k, v in COMPANY_FEEDS.items()}


@app.template_filter("format_date")
def format_date(value):
    try:
        dt = datetime.fromisoformat(value)
        return dt.strftime("%Y/%m/%d %H:%M")
    except Exception:
        return value


if __name__ == "__main__":
    os.makedirs("cache", exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)
