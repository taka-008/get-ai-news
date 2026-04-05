"""
ニュース処理エンジン
Claude APIを使ってニュースの重複排除・ランキング・要約を行う
"""
import json
import os
import anthropic
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import re

logger = logging.getLogger(__name__)

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
PROCESSED_CACHE_HOURS = 2  # 処理済みキャッシュの有効時間


def get_processed_cache_path(key: str) -> str:
    safe_key = re.sub(r"[^a-zA-Z0-9_-]", "_", key)
    return os.path.join(CACHE_DIR, f"processed_{safe_key}.json")


def load_processed_cache(key: str) -> Optional[dict]:
    path = get_processed_cache_path(key)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        cached_at = datetime.fromisoformat(data.get("cached_at", "2000-01-01"))
        if datetime.now() - cached_at > timedelta(hours=PROCESSED_CACHE_HOURS):
            return None
        return data
    except Exception:
        return None


def save_processed_cache(key: str, data: dict):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = get_processed_cache_path(key)
    data["cached_at"] = datetime.now().isoformat()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def process_news_with_claude(articles: List[Dict], context: str = "general") -> Dict:
    """
    Claude APIを使ってニュースを処理する
    - 同じトピックの記事をグループ化
    - 重要度でランキング
    - 各グループの要約を生成
    """
    if not articles:
        return {"groups": [], "updated_at": datetime.now().isoformat()}

    cache_key = f"{context}_{datetime.now().strftime('%Y%m%d_%H')}"
    cached = load_processed_cache(cache_key)
    if cached:
        return cached

    client = anthropic.Anthropic()

    # 記事リストをテキスト化（上位50件まで）
    articles_text = ""
    for i, article in enumerate(articles[:50], 1):
        articles_text += f"""
[{i}] タイトル: {article['title']}
    ソース: {article['source']}
    概要: {article['summary'][:200] if article['summary'] else '（概要なし）'}
    URL: {article['url']}
"""

    if context == "general":
        system_prompt = """あなたはAIニュースのキュレーターです。
提供されたニュース記事を分析し、以下を行ってください：
1. 同じまたは類似したトピックの記事をグループ化する
2. 各グループを重要度・話題性でランキングする
3. 各グループの簡潔な日本語要約を作成する

必ずJSON形式で出力してください。"""

        user_prompt = f"""以下のAI関連ニュース記事を分析してください。

{articles_text}

以下のJSON形式で結果を返してください：
{{
  "groups": [
    {{
      "rank": 1,
      "topic": "トピックのタイトル（日本語）",
      "summary": "このトピックの要約（200字以内、日本語）",
      "importance": "high/medium/low",
      "article_indices": [1, 2, 3],
      "category": "カテゴリ（例：新モデル/業界動向/研究/製品/規制）"
    }}
  ]
}}

重要なAIニュースのグループを最大15件、重要度の高い順に並べてください。
同一トピックの記事は必ず同じグループにまとめてください。"""

    else:
        # 企業別処理
        company_name = context
        system_prompt = f"""あなたは{company_name}に関するAIニュースのアナリストです。
提供されたニュース記事を分析し、{company_name}の最新動向を整理してください。"""

        user_prompt = f"""以下の{company_name}に関するニュース記事を分析してください。

{articles_text}

以下のJSON形式で結果を返してください：
{{
  "groups": [
    {{
      "rank": 1,
      "topic": "トピックのタイトル（日本語）",
      "summary": "このトピックの要約（200字以内、日本語）",
      "importance": "high/medium/low",
      "article_indices": [1, 2, 3],
      "category": "カテゴリ（例：新製品/パートナーシップ/研究/財務/人材）"
    }}
  ]
}}

{company_name}の最新ニュースを最大10件、重要度の高い順に返してください。"""

    try:
        with client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=4096,
            thinking={"type": "adaptive"},
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        ) as stream:
            response = stream.get_final_message()

        # レスポンスからJSONを抽出
        result_text = ""
        for block in response.content:
            if block.type == "text":
                result_text = block.text
                break

        # JSONブロックを抽出
        json_match = re.search(r'\{[\s\S]*\}', result_text)
        if json_match:
            parsed = json.loads(json_match.group())
        else:
            parsed = json.loads(result_text)

        # 記事インデックスを実際の記事データに変換
        groups_with_articles = []
        for group in parsed.get("groups", []):
            group_articles = []
            for idx in group.get("article_indices", []):
                if 1 <= idx <= len(articles):
                    group_articles.append(articles[idx - 1])
            group["articles"] = group_articles
            groups_with_articles.append(group)

        result = {
            "groups": groups_with_articles,
            "updated_at": datetime.now().isoformat(),
            "total_articles": len(articles),
        }

        save_processed_cache(cache_key, result)
        return result

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}\nResponse: {result_text[:500]}")
        # フォールバック：シンプルなリスト返却
        return _fallback_grouping(articles)
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        return _fallback_grouping(articles)


def _fallback_grouping(articles: List[Dict]) -> Dict:
    """Claude API失敗時のフォールバック処理"""
    groups = []
    for i, article in enumerate(articles[:15], 1):
        groups.append({
            "rank": i,
            "topic": article["title"],
            "summary": article["summary"][:200] if article["summary"] else "概要なし",
            "importance": "medium",
            "article_indices": [i],
            "articles": [article],
            "category": "AI",
        })
    return {
        "groups": groups,
        "updated_at": datetime.now().isoformat(),
        "total_articles": len(articles),
        "fallback": True,
    }
