# 入力欄とボタン
st.text_area("研究課題番号を入力（改行またはコンマ区切り）", key="input_area")

col1, col2 = st.columns([1, 1])
get_button = col1.button("取得する")
clear_button = col2.button("クリア")

# クリアボタン処理
if clear_button:
    st.session_state["input_area"] = ""
