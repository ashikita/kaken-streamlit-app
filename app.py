import streamlit as st
import requests
import xml.etree.ElementTree as ET

st.title("JPCOARスキーマ科研費助成情報取得ツール")

if "project_ids_input" not in st.session_state:
    st.session_state.project_ids_input = ""

st.text_area("研究課題番号を入力（改行区切り）", key="project_ids_input")

col1, col2 = st.columns([1, 1])
with col1:
    get_button = st.button("取得する")
with col2:
    clear_button = st.button("クリア")

if clear_button:
    st.session_state.project_ids_input = ""

if get_button and st.session_state.project_ids_input.strip():
    project_ids = st.session_state.project_ids_input.strip().splitlines()
    appid = st.secrets["KAKEN_APPID"] if "KAKEN_APPID" in st.secrets else "XaVdNh6thZ1gCbDmJ0Hn"

    funder_info = """    <jpcoar:funderIdentifier funderIdentifierType=\"Crossref Funder\" funderIdentifierTypeURI=\"https://www.crossref.org/services/funder-registry/\">\n        https://doi.org/10.13039/501100001691\n    </jpcoar:funderIdentifier>
    <jpcoar:funderName xml:lang=\"en\">Japan Society for the Promotion of Science (JSPS)</jpcoar:funderName>
    <jpcoar:funderName xml:lang=\"ja\">日本学術振興会</jpcoar:funderName>
    <jpcoar:fundingStreamIdentifier fundingStreamIdentifierType=\"\" fundingStreamIdentifierTypeURI=\"\"></jpcoar:fundingStreamIdentifier>
    <jpcoar:fundingStream xml:lang=\"\"></jpcoar:fundingStream>"""

    all_blocks = ""

    for raw_project_id in project_ids:
        project_id = raw_project_id.removeprefix("JP")
        award_number_type = "JGN" if raw_project_id.startswith("JP") else ""
        url = f"https://kaken.nii.ac.jp/opensearch/?appid={appid}&format=xml&qb={project_id}"

        try:
            response = requests.get(url)
            root = ET.fromstring(response.content)
        except Exception as e:
            st.warning(f"取得失敗: {raw_project_id} ({e})")
            continue

        titles = {}
        award_uri = ""

        grant_award = root.find(".//grantAward")
        if grant_award is not None:
            url_elem = grant_award.find(".//urlList/url")
            if url_elem is not None:
                award_uri = url_elem.text.strip()
            for summary in grant_award.findall(".//summary"):
                lang = summary.attrib.get("{http://www.w3.org/XML/1998/namespace}lang")
                title_elem = summary.find("title")
                if title_elem is not None:
                    titles[lang] = title_elem.text

        if not titles:
            st.warning(f"研究課題が見つかりませんでした: {raw_project_id}")
            continue

        title_ja = titles.get("ja", "")
        title_en = titles.get("en", "")

        xml_block = f"""<jpcoar:fundingReference>
{funder_info}
    <jpcoar:awardNumber awardNumberType=\"{award_number_type}\" awardURI=\"{award_uri}\">{raw_project_id}</jpcoar:awardNumber>"""
        if title_en:
            xml_block += f"\n    <jpcoar:awardTitle xml:lang=\"en\">{title_en}</jpcoar:awardTitle>"
        if title_ja:
            xml_block += f"\n    <jpcoar:awardTitle xml:lang=\"ja\">{title_ja}</jpcoar:awardTitle>"
        xml_block += "\n</jpcoar:fundingReference>\n"

        all_blocks += xml_block

    if all_blocks:
        st.code(all_blocks.strip(), language="xml")
