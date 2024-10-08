from pypdf import PdfReader, PdfWriter
import io
import streamlit as st

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

# PDFファイルをアップロード
uploaded_file = st.file_uploader("PDFファイルをアップロードしてください", type="pdf")

if uploaded_file is not None:
    try:
        if st.button("処理開始"):
            output_pdf_stream = rearrange_and_rotate_pdf(uploaded_file)
            st.write("PDFの操作が完了しました。以下に表示します。")
            st.download_button(
                label="ダウンロード PDF",
                data=output_pdf_stream,
                file_name="rearranged_rotated.pdf",
                mime="application/pdf"
            )
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")

st.write("家庭用プリンターでは冊子の形を作れません。しかし、このアプリでPDFを編集し２in１で印刷すれば家庭用プリンターでも冊子を作ることができます。")