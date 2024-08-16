import streamlit as st
from pypdf import PdfReader, PdfWriter
import tempfile
import zipfile
import os

def generate_page_order(n):
    order = []
    for i in range(1, n // 2 + 1):
        order.append(i)
        order.append(n - i + 1)
    return order

def rearrange_and_rotate_pdf(input_pdf, output_pdf_path):
    # PDFファイルを読み込む
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    # ページ数が4の倍数か確認
    num_pages = len(reader.pages)
    if num_pages < 4 or num_pages % 4 != 0:
        raise ValueError("ページ数は4の倍数である必要があります。")

    # 指定のパターンでページの順番を生成
    page_order = generate_page_order(num_pages)

    # 新しい順番でページを追加し、3と4の倍数ページを回転させる
    for i, page_num in enumerate(page_order):
        page = reader.pages[page_num - 1]

        # 新しい順番における3の倍数または4の倍数のページを回転させる
        if (i + 1) % 3 == 0 or (i + 1) % 4 == 0:
            page.rotate(180)

        writer.add_page(page)

    # 出力ファイルとして保存
    with open(output_pdf_path, "wb") as output_pdf_file:
        writer.write(output_pdf_file)

st.title("PDF 編集アプリ")

uploaded_files = st.file_uploader("PDFファイルをアップロードしてください", type="pdf", accept_multiple_files=True)
if uploaded_files:
    option = st.radio("ダウンロード方法を選択してください", ('個別でダウンロード', 'Zipで一括ダウンロード'))

    # 一時ディレクトリを用意
    with tempfile.TemporaryDirectory() as tmpdir:
        output_files = []
        for uploaded_file in uploaded_files:
            input_pdf_path = os.path.join(tmpdir, uploaded_file.name)
            with open(input_pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            output_pdf_path = os.path.join(tmpdir, f"edited_{uploaded_file.name}")
            rearrange_and_rotate_pdf(input_pdf_path, output_pdf_path)
            output_files.append(output_pdf_path)

        if option == '個別でダウンロード':
            for output_file in output_files:
                with open(output_file, "rb") as f:
                    st.download_button(
                        label=f"{os.path.basename(output_file)} をダウンロード",
                        data=f,
                        file_name=os.path.basename(output_file)
                    )

        elif option == 'Zipで一括ダウンロード':
            zip_output_path = os.path.join(tmpdir, "edited_pdfs.zip")
            with zipfile.ZipFile(zip_output_path, 'w') as zipf:
                for output_file in output_files:
                    zipf.write(output_file, arcname=os.path.basename(output_file))

            with open(zip_output_path, "rb") as f:
                st.download_button(
                    label="すべての編集されたPDFをZipでダウンロード",
                    data=f,
                    file_name="edited_pdfs.zip"
                )

st.write("家庭用プリンターでは冊子の形を作れません。しかし、このアプリでPDFを編集し２in１で印刷すれば家庭用プリンターでも冊子を作ることができます。")