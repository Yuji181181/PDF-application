from PyPDF2 import PdfReader, PdfWriter
import io
import streamlit as st
import zipfile

def generate_page_order(n):
    order = []
    for i in range(n // 2):
        order.append(n - i)  # 後半のページ
        order.append(i + 1)  # 前半のページ
    return order

def rearrange_and_rotate_pdf(input_pdf_stream):
    reader = PdfReader(input_pdf_stream)
    writer = PdfWriter()

    num_pages = len(reader.pages)
    if num_pages % 4 != 0:
        raise ValueError("ページ数は4の倍数である必要があります。")

    page_order = generate_page_order(num_pages)

    pages_to_rotate = []
    for i in range(num_pages):
        if (i + 1) % 4 == 3 or (i + 1) % 4 == 0:
            pages_to_rotate.append(page_order[i])

    for page_num in page_order:
        page = reader.pages[page_num - 1]
        if page_num in pages_to_rotate:
            page.rotate(180)
        writer.add_page(page)

    output_stream = io.BytesIO()
    writer.write(output_stream)
    output_stream.seek(0)
    return output_stream

def process_multiple_pdfs(uploaded_files):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for uploaded_file in uploaded_files:
            try:
                output_pdf_stream = rearrange_and_rotate_pdf(uploaded_file)
                zip_file.writestr(uploaded_file.name, output_pdf_stream.read())
            except ValueError as ve:
                st.error(f"{uploaded_file.name} でエラーが発生しました: {ve}")
            except Exception as e:
                st.error(f"{uploaded_file.name} でエラーが発生しました: {e}")
    
    zip_buffer.seek(0)
    return zip_buffer

# Streamlitアプリケーション
st.title("同人誌PDFクリエイター")

# PDFファイルをアップロード
uploaded_files = st.file_uploader(
    "PDFファイルをアップロードしてください", type="pdf", accept_multiple_files=True)

if uploaded_files is not None and len(uploaded_files) > 0:
    if st.button("処理開始"):
        try:
            zip_buffer = process_multiple_pdfs(uploaded_files)
            st.success("PDFの操作が完了しました。以下に表示します。")
            st.download_button(
                label="ダウンロード ZIP",
                data=zip_buffer,
                file_name="rearranged_rotated_pdfs.zip",
                mime="application/zip"
            )
        except Exception as e:
            st.error(f"一括処理中にエラーが発生しました: {e}")

st.write("家庭用プリンターでは冊子の形を作れません。しかし、このアプリでPDFを編集し２in１で印刷すれば家庭用プリンターでも冊子を作ることができます。")