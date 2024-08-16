from pypdf import PdfReader, PdfWriter
import io
import streamlit as st
import zipfile

def generate_page_order(n):
    order = []
    for i in range(n // 2):
        order.append(n - i)      # 後半のページ
        order.append(i + 1)      # 前半のページ
    return order

def rearrange_and_rotate_pdf(input_pdf_stream):
    reader = PdfReader(input_pdf_stream)
    writer = PdfWriter()

    num_pages = len(reader.pages)
    if num_pages % 4 != 0:
        raise ValueError("ページ数は4の倍数である必要があります。")

    # ページ順の生成
    page_order = generate_page_order(num_pages)

    # 回転が必要なページを計算
    pages_to_rotate = []
    for i in range(num_pages):
        if (i + 1) % 4 == 3 or (i + 1) % 4 == 0:
            pages_to_rotate.append(page_order[i])

    for page_num in page_order:
        page = reader.pages[page_num - 1]

        # 回転が必要なページを回転させる
        if page_num in pages_to_rotate:
            page.rotate(180)

        writer.add_page(page)

    output_stream = io.BytesIO()
    writer.write(output_stream)
    output_stream.seek(0)
    return output_stream

# Streamlitアプリケーション
st.title("同人誌PDFクリエイター")

# 複数のPDFファイルをアップロード
uploaded_files = st.file_uploader("PDFファイルをアップロードしてください", type="pdf", accept_multiple_files=True)

if uploaded_files:
    pdf_buffers = []
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for uploaded_file in uploaded_files:
            try:
                # PDFの処理
                output_pdf_stream = rearrange_and_rotate_pdf(uploaded_file)

                # PDFの個別ダウンロードボタンを表示
                st.download_button(
                    label=f"ダウンロード {uploaded_file.name}",
                    data=output_pdf_stream,
                    file_name=f"rearranged_rotated_{uploaded_file.name}",
                    mime="application/pdf"
                )

                # ZIPに追加
                pdf_buffers.append((f"rearranged_rotated_{uploaded_file.name}", output_pdf_stream.getvalue()))
            except Exception as e:
                st.error(f"ファイル {uploaded_file.name} の処理中にエラーが発生しました: {e}")

    # すべてのPDFをZIPに追加
    for file_name, pdf_data in pdf_buffers:
        zip_file.writestr(file_name, pdf_data)

    zip_buffer.seek(0)

    # ZIPファイルをダウンロードするボタンを表示
    st.download_button(
        label="すべてをZIPとしてダウンロード",
        data=zip_buffer,
        file_name="rearranged_pdfs.zip",
        mime="application/zip"
    )

st.write("家庭用プリンターでは冊子の形を作れません。しかし、このアプリでPDFを編集し２in１で印刷すれば家庭用プリンターでも冊子を作ることができます。")
