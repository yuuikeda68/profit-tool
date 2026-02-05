import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime

# ページ設定
st.set_page_config(page_title="フリマ利益計算ツール", page_icon="💰", layout="wide")

# =============================================
# パスワード認証
# =============================================
CORRECT_PASSWORD = "orange2026"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("フリマ利益計算ツール")
    st.markdown("---")
    password = st.text_input("パスワードを入力してください", type="password")
    if password:
        if password == CORRECT_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("パスワードが正しくありません。")
    st.stop()

# =============================================
# 以下、認証後のみ表示
# =============================================

# プラットフォーム定義（名前, 手数料率）
PLATFORMS = {
    "メルカリ": 0.10,
    "ラクマ": 0.066,
    "PayPayフリマ": 0.05,
}

# --- セッションステートで履歴を保持 ---
if "history" not in st.session_state:
    st.session_state.history = []


def copy_button(label, value, key):
    """販売価格の横にクリップボードコピーボタンを表示する"""
    components.html(
        f"""
        <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
            <span style="font-size:1.5rem; font-weight:bold; color:#333;">
                {label}
            </span>
            <button id="btn-{key}" onclick="
                navigator.clipboard.writeText('{value}').then(function() {{
                    var btn = document.getElementById('btn-{key}');
                    btn.textContent = 'Copied!';
                    btn.style.background = '#0f9d58';
                    setTimeout(function() {{
                        btn.textContent = 'コピー';
                        btn.style.background = '#ff4b4b';
                    }}, 1500);
                }});
            " style="
                background: #ff4b4b;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 1rem;
                font-weight: bold;
                cursor: pointer;
                min-width: 90px;
                min-height: 44px;
                touch-action: manipulation;
            ">コピー</button>
        </div>
        """,
        height=55,
    )


# --- スタイル ---
st.markdown("""
<style>
    .profit-positive { color: #0f9d58; font-size: 1.6rem; font-weight: bold; }
    .profit-negative { color: #db4437; font-size: 1.6rem; font-weight: bold; }
    .metric-label { color: #888; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

st.title("フリマ利益計算ツール")
st.caption("メルカリ / ラクマ / PayPayフリマ の手数料・利益を一括比較")

# --- サイドバー：共通入力 ---
st.sidebar.header("共通設定")
product_name = st.sidebar.text_input("商品名", value="", placeholder="例: ワイヤレスイヤホン")
selling_price = st.sidebar.number_input("販売価格 (円)", min_value=0, value=2000, step=100)
shipping_cost = st.sidebar.number_input("送料 (円)", min_value=0, value=210, step=10)
cost_price = st.sidebar.number_input("仕入れ値 (円)", min_value=0, value=500, step=50)

# --- タブ構成 ---
tab1, tab2 = st.tabs(["📊 販売価格 → 利益を計算", "🎯 目標利益 → 販売価格を逆算"])

# =============================================
# タブ1: 販売価格 → 利益計算
# =============================================
with tab1:
    cols = st.columns(3)
    results = []

    for col, (name, rate) in zip(cols, PLATFORMS.items()):
        fee = int(selling_price * rate)
        profit = selling_price - fee - shipping_cost - cost_price
        profit_margin = (profit / selling_price * 100) if selling_price > 0 else 0

        results.append({
            "プラットフォーム": name,
            "手数料率": f"{rate*100:.1f}%",
            "手数料": fee,
            "送料": shipping_cost,
            "仕入れ値": cost_price,
            "利益": profit,
            "利益率": f"{profit_margin:.1f}%",
        })

        with col:
            st.markdown(f"### {name}（手数料 {rate*100:.1f}%）")
            copy_button(f"¥{selling_price:,}", selling_price, f"tab1_{name}")
            st.metric("手数料", f"¥{fee:,}")
            css_class = "profit-positive" if profit >= 0 else "profit-negative"
            st.markdown(
                f'<span class="metric-label">利益</span><br>'
                f'<span class="{css_class}">¥{profit:,}（利益率 {profit_margin:.1f}%）</span>',
                unsafe_allow_html=True,
            )
            st.divider()
            st.caption(f"内訳: 売上 ¥{selling_price:,} − 手数料 ¥{fee:,} − 送料 ¥{shipping_cost:,} − 仕入 ¥{cost_price:,}")

    # 比較テーブル
    st.subheader("比較一覧")
    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # 履歴に追加ボタン
    if st.button("この計算結果を履歴に追加", key="add_history_tab1", type="primary"):
        label = product_name if product_name else "未設定"
        for name, rate in PLATFORMS.items():
            fee = int(selling_price * rate)
            profit = selling_price - fee - shipping_cost - cost_price
            profit_margin = (profit / selling_price * 100) if selling_price > 0 else 0
            st.session_state.history.append({
                "記録日時": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "商品名": label,
                "計算タイプ": "販売価格→利益",
                "プラットフォーム": name,
                "販売価格": selling_price,
                "手数料": fee,
                "送料": shipping_cost,
                "仕入れ値": cost_price,
                "利益": profit,
                "利益率": f"{profit_margin:.1f}%",
            })
        st.success(f"「{label}」の計算結果を履歴に追加しました！")

# =============================================
# タブ2: 目標利益 → 販売価格を逆算
# =============================================
with tab2:
    target_profit = st.number_input(
        "目標利益 (円)", min_value=0, value=1000, step=100, key="tab2_profit"
    )

    st.info(
        "計算式: **販売価格 = (目標利益 + 送料 + 仕入れ値) ÷ (1 − 手数料率)**"
    )

    cols2 = st.columns(3)
    reverse_results = []

    for col, (name, rate) in zip(cols2, PLATFORMS.items()):
        required_price = (target_profit + shipping_cost + cost_price) / (1 - rate)
        required_price_rounded = int(required_price) + (1 if required_price % 1 > 0 else 0)
        actual_fee = int(required_price_rounded * rate)
        actual_profit = required_price_rounded - actual_fee - shipping_cost - cost_price

        reverse_results.append({
            "プラットフォーム": name,
            "手数料率": f"{rate*100:.1f}%",
            "必要販売価格": required_price_rounded,
            "手数料": actual_fee,
            "実際の利益": actual_profit,
        })

        with col:
            st.markdown(f"### {name}（手数料 {rate*100:.1f}%）")
            st.caption("必要な販売価格")
            copy_button(f"¥{required_price_rounded:,}", required_price_rounded, f"tab2_{name}")
            st.caption(
                f"この価格で売ると → 手数料 ¥{actual_fee:,} / 利益 ¥{actual_profit:,}"
            )

    # 比較テーブル
    st.subheader("逆算比較一覧")
    df2 = pd.DataFrame(reverse_results)
    st.dataframe(df2, use_container_width=True, hide_index=True)

    # 履歴に追加ボタン
    if st.button("この計算結果を履歴に追加", key="add_history_tab2", type="primary"):
        label = product_name if product_name else "未設定"
        for name, rate in PLATFORMS.items():
            required_price = (target_profit + shipping_cost + cost_price) / (1 - rate)
            required_price_rounded = int(required_price) + (1 if required_price % 1 > 0 else 0)
            actual_fee = int(required_price_rounded * rate)
            actual_profit = required_price_rounded - actual_fee - shipping_cost - cost_price
            st.session_state.history.append({
                "記録日時": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "商品名": label,
                "計算タイプ": "目標利益→逆算",
                "プラットフォーム": name,
                "販売価格": required_price_rounded,
                "手数料": actual_fee,
                "送料": shipping_cost,
                "仕入れ値": cost_price,
                "利益": actual_profit,
                "利益率": f"{(actual_profit / required_price_rounded * 100):.1f}%",
            })
        st.success(f"「{label}」の逆算結果を履歴に追加しました！")

# =============================================
# 履歴セクション（常に画面下部に表示）
# =============================================
st.divider()
st.subheader("計算履歴")

if st.session_state.history:
    df_history = pd.DataFrame(st.session_state.history)
    st.dataframe(df_history, use_container_width=True, hide_index=True)

    # CSV ダウンロード & 履歴クリアを横並び
    col_dl, col_clear, _ = st.columns([1, 1, 3])
    with col_dl:
        csv = df_history.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="CSV ダウンロード",
            data=csv,
            file_name=f"利益計算履歴_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )
    with col_clear:
        if st.button("履歴をクリア"):
            st.session_state.history = []
            st.rerun()
else:
    st.caption("まだ履歴がありません。計算後に「履歴に追加」ボタンを押すと記録されます。")

# --- フッター ---
st.divider()
st.caption("※ 手数料率 — メルカリ: 10%, ラクマ: 6.6%, PayPayフリマ: 5% で計算しています。")
