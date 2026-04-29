import streamlit as st
from docx import Document
from docx.shared import Pt
import google.generativeai as genai
import io

st.set_page_config(page_title="Dịch Word Trung-Việt", layout="centered")

st.title("📱 App Dịch Word Song Ngữ")

# 1. Nhập API Key
api_key = st.text_input("Nhập Gemini API Key:", type="password")

# 2. Lựa chọn hình thức dịch
mode = st.radio("Hình thức dịch:", ("Song ngữ (Trung-Việt)", "Chỉ Tiếng Việt"))

# 3. Gắn file Word
uploaded_file = st.file_uploader("Chọn tập tin Word (.docx)", type="docx")

if uploaded_file is not None and api_key:
    if st.button("🚀 BẮT ĐẦU DỊCH"):
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            # Đọc file Word từ bộ nhớ đệm
            doc = Document(uploaded_file)
            
            st.info("Đang dịch... Vui lòng đợi trong giây lát.")
            
            def process_text(para):
                if para.text.strip():
                    resp = model.generate_content(f"Dịch sang tiếng Việt: {para.text}")
                    translated = resp.text.strip()
                    if "Song ngữ" in mode:
                        para.add_run(f"\n{translated}").font.name = 'Times New Roman'
                        para.runs[-1].font.size = Pt(11)
                        para.runs[-1].italic = True
                    else:
                        para.text = translated
                        for run in para.runs: run.font.name = 'Times New Roman'

            # Xử lý văn bản
            for p in doc.paragraphs: process_text(p)
            for t in doc.tables:
                for r in t.rows:
                    for c in r.cells:
                        for p in c.paragraphs: process_text(p)

            # Lưu file vào bộ nhớ để tải về
            bio = io.BytesIO()
            doc.save(bio)
            
            st.success("Dịch xong rực rỡ!")
            st.download_button(
                label="📥 TẢI FILE ĐÃ DỊCH VỀ ĐIỆN THOẠI",
                data=bio.getvalue(),
                file_name="Ban_Dich_Song_Ngu.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        except Exception as e:
            st.error(f"Lỗi: {e}")
