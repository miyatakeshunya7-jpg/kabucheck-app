import streamlit as st
import pandas as pd
import yfinance as yf
import random
import plotly.express as px  # Plotlyのインポート

# ページの設定
st.set_page_config(
    page_title="日本株・全市場AIスクリーニング＆ポートフォリオ",
    page_icon="📈",
    layout="wide"
)

st.title("📈 日本株 AIスクリーニング ＆ ポートフォリオ分析アプリ")
st.markdown("市場全体のランキング、まだ見ぬ銘柄の発掘、保有銘柄のチャート分析、そして詳細なインタラクティブ散布図で銘柄を分析できます。")

# 1. 市場全体の主要主力銘柄プール
CORE_MARKET_POOL = {
    "7203.T": "自動車・モビリティ", "7267.T": "自動車・モビリティ", "6902.T": "自動車・モビリティ",
    "8035.T": "半導体", "6861.T": "半導体", "4063.T": "半導体・素材", "6762.T": "電子部品", "6981.T": "電子部品",
    "9984.T": "AI・投資", "6758.T": "エンタメ・テック", "7974.T": "エンタメ・テック", "9432.T": "通信・DX", "9433.T": "通信・DX",
    "8306.T": "金融", "8316.T": "金融", "8411.T": "金融", "8766.T": "金融・保険",
    "8058.T": "商社・資源", "8031.T": "商社・資源", "8001.T": "商社・資源", "8053.T": "商社・資源",
    "6501.T": "インフラ・DX", "6503.T": "インフラ・DX", "7011.T": "重工業", "6301.T": "機械", "5401.T": "鉄鋼・素材", "5020.T": "エネルギー",
    "4502.T": "医薬品", "4503.T": "医薬品", "4568.T": "医薬品", "2914.T": "食品・たばこ", "3382.T": "小売", "4901.T": "化学・消費財",
    "4661.T": "レジャー", "6098.T": "人材・サービス", "8802.T": "不動産"
}

# 2. まだ見ぬ銘柄を発掘するための予備プール
DISCOVERY_POOL = {
    "6525.T": "半導体", "6857.T": "半導体", "6146.T": "半導体", "6723.T": "半導体",
    "7272.T": "自動車・モビリティ", "6594.T": "モーター・テック", "9983.T": "小売・DX", "4755.T": "ネットサービス",
    "8308.T": "金融", "8604.T": "金融", "7182.T": "金融", "8591.T": "金融",
    "8002.T": "商社・資源", "8015.T": "商社・資源", "7012.T": "重工業", "7013.T": "重工業",
    "6367.T": "機械", "6954.T": "機械", "5801.T": "素材", "5802.T": "素材", "5803.T": "素材", "3436.T": "素材",
    "4519.T": "医薬品", "4578.T": "医薬品", "2802.T": "食品", "4452.T": "化学・消費財", "5108.T": "消費財",
    "2413.T": "ネットサービス", "9501.T": "エネルギー", "3038.T": "小売", "3099.T": "小売", "4689.T": "ネットサービス"
}

# セッション状態の初期化
if "discovery_list" not in st.session_state:
    disc_items = list(DISCOVERY_POOL.items())
    st.session_state.discovery_list = dict(random.sample(disc_items, min(15, len(disc_items))))

if "portfolio_list" not in st.session_state:
    st.session_state.portfolio_list = ["7203.T", "6758.T"]

# ==========================================
# 🛠️ サイドバー：検索・追加・保有銘柄・シャッフル管理
# ==========================================
st.sidebar.header("➕ 個別銘柄の追加・検索")
new_code_input = st.sidebar.text_input("証券コード (例: 7974 または 7974.T)", "").strip()
new_theme_input = st.sidebar.selectbox(
    "成長産業テーマを選択", 
    ["AI・投資", "半導体", "自動車・モビリティ", "通信・DX", "エネルギー", "金融", "エンタメ・テック", "インフラ・DX", "半導体・素材", "商社・資源", "医薬品", "その他"]
)

if st.sidebar.button("市場プールに追加"):
    if new_code_input:
        f_code = new_code_input if new_code_input.endswith(".T") else new_code_input + ".T"
        CORE_MARKET_POOL[f_code] = new_theme_input
        st.sidebar.success(f"{f_code} を市場プールに追加しました！")
        st.cache_data.clear()
        st.rerun()
    else:
        st.sidebar.error("証券コードを入力してください。")

st.sidebar.markdown("---")
st.sidebar.header("💼 保有銘柄（チャート表示用）")
port_code_input = st.sidebar.text_input("保有銘柄コード追加 (例: 7974)", "").strip()
if st.sidebar.button("保有銘柄に追加"):
    if port_code_input:
        p_code = port_code_input if port_code_input.endswith(".T") else port_code_input + ".T"
        if p_code not in st.session_state.portfolio_list:
            st.session_state.portfolio_list.append(p_code)
            st.sidebar.success(f"{p_code} を保有銘柄に登録しました！")
            st.rerun()
        else:
            st.sidebar.warning("すでに登録されています。")

if st.session_state.portfolio_list:
    remove_target = st.sidebar.selectbox("保有銘柄から削除", ["選択してください"] + st.session_state.portfolio_list)
    if remove_target != "選択してください" and st.sidebar.button("選択した銘柄を削除"):
        st.session_state.portfolio_list.remove(remove_target)
        st.sidebar.success(f"{remove_target} を削除しました。")
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("🎲 発掘プールの更新")
if st.sidebar.button("まだ見ぬオススメ銘柄をシャッフル"):
    disc_items = list(DISCOVERY_POOL.items())
    st.session_state.discovery_list = dict(random.sample(disc_items, min(15, len(disc_items))))
    st.cache_data.clear()
    st.rerun()

# ==========================================
# 📊 データ取得・AIスコアリング関数
# ==========================================
@st.cache_data(ttl=3600)
def fetch_and_score_stocks(core_dict, disc_dict, port_list):
    port_dict = {code: "保有銘柄" for code in port_list}
    combined = {**core_dict, **disc_dict, **port_dict}
    data_list = []
    news_dict = {}
    
    for ticker_symbol, theme in combined.items():
        try:
            stock = yf.Ticker(ticker_symbol)
            info = stock.info
            
            name = info.get("longName", ticker_symbol)
            current_price = info.get("currentPrice", info.get("regularMarketPrice", 0))
            
            rev_growth = info.get("revenueGrowth", 0)
            rev_growth_pct = round(rev_growth * 100, 2) if rev_growth else 0.0
            
            debt_to_equity = info.get("debtToEquity", 50)
            
            dividend_yield = info.get("dividendYield", 0)
            dividend_yield_pct = round(dividend_yield * 100, 2) if dividend_yield else 0.0
            payout_ratio = info.get("payoutRatio", 0)
            payout_pct = round(payout_ratio * 100, 1) if payout_ratio else 0.0
            
            per = info.get("trailingPE", 0)
            per_val = round(per, 1) if per else 0.0

            # AIスコアリングロジック (100点満点)
            score_growth = min(max(rev_growth_pct, 0) * 1.5, 35)
            score_dividend = min(dividend_yield_pct * 5, 25)
            if 30 <= payout_pct <= 65:
                score_dividend += 5
                
            if 10 <= per_val <= 25:
                score_val = 20
            elif 0 < per_val < 10:
                score_val = 15
            else:
                score_val = 5
                
            score_safety = 15 if debt_to_equity < 100 else 10

            total_ai_score = round(score_growth + score_dividend + score_val + score_safety, 1)

            if dividend_yield_pct >= 2.5 or (score_safety >= 15 and per_val <= 20):
                style = "長期保有向き"
            else:
                style = "短期保有向き"
                
            if ticker_symbol in port_list:
                category = "保有銘柄"
            elif ticker_symbol in core_dict:
                category = "市場全体（主力）"
            else:
                category = "まだ見ぬオススメ枠"

            data_list.append({
                "銘柄コード": ticker_symbol.replace(".T", ""),
                "銘柄名": name,
                "フルコード": ticker_symbol,
                "カテゴリ": category,
                "成長産業テーマ": theme,
                "推奨スタイル": style,
                "AI総合スコア": total_ai_score,
                "株価(円)": current_price,
                "売上成長率(%)": rev_growth_pct,
                "配当利回り(%)": dividend_yield_pct,
                "PER(倍)": per_val
            })
            
            raw_news = stock.news
            if raw_news:
                news_list = []
                for item in raw_news[:3]:
                    news_list.append({
                        "title": item.get("title", "タイトルなし"),
                        "publisher": item.get("publisher", "不明"),
                        "link": item.get("link", "#")
                    })
                news_dict[ticker_symbol.replace(".T", "")] = news_list
                
        except Exception:
            continue
            
    return pd.DataFrame(data_list), news_dict

# データ読み込み
with st.spinner("市場全体のデータおよび保有銘柄の情報を取得中..."):
    df, stock_news = fetch_and_score_stocks(CORE_MARKET_POOL, st.session_state.discovery_list, st.session_state.portfolio_list)

if df.empty:
    st.error("データを取得できませんでした。")
else:
    # ==========================================
    # 📱 メイン画面の表示
    # ==========================================
    
    # 0. 保有銘柄のチャート＆一覧
    st.markdown("### 💼 あなたの保有銘柄・ポートフォリオ分析")
    portfolio_df = df[df["カテゴリ"] == "保有銘柄"]
    if not portfolio_df.empty:
        st.dataframe(portfolio_df.drop(columns=["フルコード", "カテゴリ"]), use_container_width=True)
        
        st.markdown("#### 📉 保有銘柄の株価チャート（過去1年）")
        for _, row in portfolio_df.iterrows():
            code = row["銘柄コード"]
            full_code = row["フルコード"]
            name = row["銘柄名"]
            
            with st.expander(f"📈 銘柄チャート: {code} - {name}"):
                try:
                    hist_data = yf.Ticker(full_code).history(period="1y")
                    if not hist_data.empty:
                        st.line_chart(hist_data["Close"])
                    else:
                        st.info("チャートデータを取得できませんでした。")
                except Exception:
                    st.error("チャート描画中にエラーが発生しました。")
    else:
        st.info("保有銘柄が登録されていません。左側のサイドバーから証券コードを追加してください。")

    st.markdown("---")

    # 1. 市場全体の上位ランキング
    market_df = df[df["カテゴリ"] == "市場全体（主力）"]
    top_market_df = market_df.sort_values(by="AI総合スコア", ascending=False).head(50).reset_index(drop=True)
    top_market_df.index = top_market_df.index + 1
    top_market_df = top_market_df.rename_axis("順位").reset_index()

    st.markdown(f"### 👑 市場全体の上位ランキング (上位 {len(top_market_df)} 銘柄)")
    if not top_market_df.empty:
        st.dataframe(top_market_df.drop(columns=["フルコード", "カテゴリ"]), use_container_width=True)

    st.markdown("---")

    # 2. まだ見ぬオススメ銘柄
    discovery_df = df[df["カテゴリ"] == "まだ見ぬオススメ枠"]
    st.markdown("### ✨ まだ見ぬオススメ銘柄（発掘枠）")
    if not discovery_df.empty:
        disc_ranked = discovery_df.sort_values(by="AI総合スコア", ascending=False).reset_index(drop=True)
        st.dataframe(disc_ranked.drop(columns=["フルコード", "カテゴリ"]), use_container_width=True)

    st.markdown("---")

    # 3. 投資スタイル別 分類テーブル
    st.markdown("### 🏛️ 投資スタイル別 分類テーブル")
    long_term_df = df[df["推奨スタイル"] == "長期保有向き"].sort_values(by="AI総合スコア", ascending=False)
    short_term_df = df[df["推奨スタイル"] == "短期保有向き"].sort_values(by="AI総合スコア", ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🟢 【長期保有向き】安定配当・バリュー重視")
        if not long_term_df.empty:
            st.dataframe(long_term_df.drop(columns=["フルコード", "カテゴリ", "推奨スタイル"]).reset_index(drop=True), use_container_width=True)

    with col2:
        st.markdown("#### ⚡ 【短期保有向き】高成長・モメンタム重視")
        if not short_term_df.empty:
            st.dataframe(short_term_df.drop(columns=["フルコード", "カテゴリ", "推奨スタイル"]).reset_index(drop=True), use_container_width=True)

    # 4. 💡 Plotlyを使ったインタラクティブな散布図グラフ
    st.markdown("---")
    st.subheader("💡 銘柄の全体分布（配当利回り ｘ 売上成長率）")
    st.markdown("各ドットにマウスを合わせると、銘柄名や詳細情報がポップアップで表示されます。色分けは推奨スタイルに対応しています。")

    # Plotlyで散布図を作成
    fig = px.scatter(
        df,
        x="配当利回り(%)",
        y="売上成長率(%)",
        color="推奨スタイル",
        size="AI総合スコア",
        hover_name="銘柄名",
        hover_data={
            "銘柄コード": True,
            "成長産業テーマ": True,
            "AI総合スコア": True,
            "配当利回り(%)": True,
            "売上成長率(%)": True,
            "PER(倍)": True,
            "推奨スタイル": False
        },
        height=600
    )

    # グラフのレイアウト調整
    fig.update_layout(
        xaxis_title="配当利回り (%)",
        yaxis_title="売上成長率 (%)",
        legend_title="推奨スタイル"
    )

    # StreamlitにPlotlyのグラフを表示
    st.plotly_chart(fig, use_container_width=True)