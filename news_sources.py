"""
ニュースソース定義
RSSフィードのURLと企業別ソースを管理する
"""

# 一般AIニュースのRSSフィード
GENERAL_AI_FEEDS = [
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/feed/",
    },
    {
        "name": "MIT Technology Review",
        "url": "https://www.technologyreview.com/feed/",
    },
    {
        "name": "The Verge AI",
        "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    },
    {
        "name": "Wired AI",
        "url": "https://www.wired.com/feed/category/ai/latest/rss",
    },
    {
        "name": "Google News AI",
        "url": "https://news.google.com/rss/search?q=artificial+intelligence+AI&hl=ja&gl=JP&ceid=JP:ja",
    },
]

# 企業別RSSフィードと検索クエリ
COMPANY_FEEDS = {
    "openai": {
        "display_name": "OpenAI",
        "color": "#10a37f",
        "icon": "🤖",
        "feeds": [
            {
                "name": "OpenAI Blog",
                "url": "https://openai.com/blog/rss.xml",
            },
        ],
        "search_query": "OpenAI ChatGPT GPT",
        "google_news_url": "https://news.google.com/rss/search?q=OpenAI+ChatGPT&hl=ja&gl=JP&ceid=JP:ja",
    },
    "anthropic": {
        "display_name": "Anthropic",
        "color": "#cc785c",
        "icon": "🔬",
        "feeds": [
            {
                "name": "Anthropic News",
                "url": "https://www.anthropic.com/rss.xml",
            },
        ],
        "search_query": "Anthropic Claude AI",
        "google_news_url": "https://news.google.com/rss/search?q=Anthropic+Claude&hl=ja&gl=JP&ceid=JP:ja",
    },
    "google": {
        "display_name": "Google",
        "color": "#4285f4",
        "icon": "🌐",
        "feeds": [
            {
                "name": "Google AI Blog",
                "url": "https://blog.google/technology/ai/rss/",
            },
        ],
        "search_query": "Google Gemini DeepMind AI",
        "google_news_url": "https://news.google.com/rss/search?q=Google+Gemini+DeepMind+AI&hl=ja&gl=JP&ceid=JP:ja",
    },
    "copilot": {
        "display_name": "Microsoft Copilot",
        "color": "#00a4ef",
        "icon": "🪁",
        "feeds": [
            {
                "name": "Microsoft Tech Community - Copilot",
                "url": "https://techcommunity.microsoft.com/t5/microsoft-copilot-blog/bg-p/MicrosoftCopilotBlog/rss",
            },
        ],
        "search_query": "Microsoft Copilot AI",
        "google_news_url": "https://news.google.com/rss/search?q=Microsoft+Copilot&hl=ja&gl=JP&ceid=JP:ja",
    },
    "fabric": {
        "display_name": "Microsoft Fabric",
        "color": "#742774",
        "icon": "🔷",
        "feeds": [
            {
                "name": "Microsoft Fabric Blog",
                "url": "https://blog.fabric.microsoft.com/en-US/feed/",
            },
        ],
        "search_query": "Microsoft Fabric データ分析",
        "google_news_url": "https://news.google.com/rss/search?q=Microsoft+Fabric&hl=ja&gl=JP&ceid=JP:ja",
    },
    "amazon": {
        "display_name": "Amazon",
        "color": "#ff9900",
        "icon": "📦",
        "feeds": [
            {
                "name": "AWS Machine Learning Blog",
                "url": "https://aws.amazon.com/blogs/machine-learning/feed/",
            },
        ],
        "search_query": "Amazon AWS Bedrock AI",
        "google_news_url": "https://news.google.com/rss/search?q=Amazon+AWS+Bedrock+AI&hl=ja&gl=JP&ceid=JP:ja",
    },
}
