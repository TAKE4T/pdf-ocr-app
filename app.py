import streamlit as st
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import os
import tempfile

st.title("PDF OCR アプリケーション")
st.write("PDFファイルをアップロードして日本語OCRを実行します")

# Tesseractの設定（Streamlitクラウドではすでにインストールされています）
# ローカルで実行する場合はパスを設定する必要があるかもしれません
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

uploaded_file = st.file_uploader("PDFファイルをアップロード", type=["pdf"])

if uploaded_file is not None:
    # 一時ファイルとしてPDFを保存
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        pdf_path = tmp_file.name
    
    if st.button("OCRを実行"):
        with st.spinner("OCR処理中..."):
            try:
                doc = fitz.open(pdf_path)
                all_text = []
                
                progress_bar = st.progress(0)
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap(dpi=300)
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    
                    # 日本語OCRを実行
                    text = pytesseract.image_to_string(img, lang='jpn')
                    all_text.append(f"--- ページ {page_num+1} ---\n{text}\n\n")
                    
                    # 進捗バーを更新
                    progress_bar.progress((page_num + 1) / len(doc))
                
                # 結果を表示
                result_text = "".join(all_text)
                st.text_area("OCR結果", result_text, height=400)
                
                # ダウンロードボタン
                st.download_button(
                    label="テキストファイルをダウンロード",
                    data=result_text,
                    file_name=f"{uploaded_file.name}_ocr.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
            finally:
                # 一時ファイルを削除
                os.unlink(pdf_path)
