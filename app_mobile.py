import streamlit as st
from docx import Document
from docx.shared import Pt
import google.generativeai as genai
import io
import time

st.set_page_config(page_title="Dịch Word Pro", layout="centered")
st.title("📱 App Dịch Word Siêu Tốc v5.1")

# Nhập liệu
api_key = st.text_input("Nhập Gemini API Key:", type="password")
mode = st.radio("Hình thức dịch:", ("Song ngữ (Trung-Việt)", "Chỉ Tiếng Việt"))
uploaded_file = st.file_uploader("Chọn file .docx", type="docx")

if uploaded_file and api_key:
    if st.button("🚀 BẮT ĐẦU DỊCH"):
        try:
            genai.configure(api_key=api_key)
            # Sửa tên model tại đây để tránh lỗi 404
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            doc = Document(uploaded_file)
            
            paras = [p for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for p in cell.paragraphs:
                            if p.text.strip(): paras.append(p)
            
            total = len(paras)
            st.info(f"Đang xử lý {total} đoạn văn...")
            progress_bar = st.progress(0)
            
            # Gom 10 đoạn văn dịch 1 lần để tối ưu hóa
            batch_size = 10 
            for i in range(0, total, batch_size):
                batch = paras[i:i + batch_size]
                combined_text = "\n---\n".join([p.text for p in batch])
                
                prompt = f"Dịch các đoạn văn sau sang tiếng Việt. Giữ nguyên thứ tự, phân cách bằng '---'. Chỉ trả về bản dịch:\n{combined_text}"
                
                translated_batch = []
                for attempt in range(3):
                    try:
                        response = model.generate_content(prompt)
                        # Tách bản dịch dựa trên dấu phân cách
                        translated_batch = response.text.split("---")
                        break
                    except Exception as e:
                        if "429" in str(e):
                            time.sleep(12) # Nghỉ lâu hơn nếu bị quá tải
                        else:
                            st.error(f"Lỗi API: {e}")
                            st.stop()
                
                for idx, p in enumerate(batch):
                    if idx < len(translated_batch):
                        result = translated_batch[idx].strip()
                        if "Song ngữ" in mode:
                            # Chèn tiếng Việt với font Times New Roman
                            p.add_run(f"\n{result}").font.name = 'Times New Roman'
                            p.runs[-1].font.size = Pt(11)
                            p.runs[-1].italic = True
                        else:
                            p.text = result
                            for run in p.runs:
                                run.font.name = 'Times New Roman'
                
                progress_bar.progress(min((i + batch_size) / total, 1.0))
            
            bio = io.BytesIO()
            doc.save(bio)
            st.success("Đã hoàn thành!")
            st.download_button("📥 TẢI FILE VỀ ĐIỆN THOẠI", bio.getvalue(), f"Dich_{uploaded_file.name}", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            
        except Exception as e:
            st.error(f"Lỗi hệ thống: {e}")
