import time
from unstructured.partition.pdf import partition_pdf
import markdownify
from unstructured.documents.elements import Title, Table, Image
import re
filename = './code.pdf'

def starts_with_number_dot(s):
    """Check if a title starts with a number and a dot (e.g., '6.', '6.1.')."""
    pattern = r"^\d+(?:\.\d+)*\.?\s+\S.*"
    return bool(re.match(pattern, s))

def starts_with_double_slash(line):
    """Check if a line starts with '//' (comment line)."""
    return bool(re.match(r'^\s*//', line))

def check_session(elements):
    sessions = []
    contents = []
    contents_image = []
    types = []

    session = "Title 0. Begin"  # Mặc định là "Title 0. Begin" cho nội dung trước tiêu đề hợp lệ
    content = ""
    has_valid_title = False  # Biến kiểm tra xem có tiêu đề hợp lệ hay chưa

    for element in elements:
        element_str = str(element)  # Chuyển đổi sang chuỗi để xử lý nhanh hơn

        # Bỏ qua comment `//`
        if starts_with_double_slash(element_str):
            continue

        # Xử lý tiêu đề (Title)
        if isinstance(element, Title):
            if starts_with_number_dot(element.text):  # Nếu là tiêu đề hợp lệ
                if session and content:  # Lưu session trước khi đổi tiêu đề
                    sessions.append(session)
                    contents.append(content)
                    types.append("Text")

                session = f"Title: {element.text}"
                content = ""  # Reset nội dung cho session mới
                has_valid_title = True  # Đánh dấu đã có tiêu đề hợp lệ
            else:  # Nếu là tiêu đề nhưng không hợp lệ (không bắt đầu bằng số)
                content += f"Title: {element.text}\n"  # Ghi lại vào nội dung "Title 0. Begin"
            continue  # Không xử lý `Title` như nội dung

        # Xử lý bảng (Table)
        if isinstance(element, Table):
            html_content = element.metadata.text_as_html  # Lấy HTML từ metadata
            # markdown_table = markdownify.markdownify(html_content)

            if has_valid_title:
                sessions.append(session)
                contents.append(content)  # Lưu nội dung hiện tại trước khi thêm bảng
                types.append("Text")

                sessions.append(session)  # Giữ cùng session nhưng thêm bảng
                # contents.append(markdown_table)
                contents.append(html_content)
                types.append("Table")
                content = ""  # Reset nội dung sau khi thêm bảng
            else:
                contents.append(html_content)  # Nếu chưa có tiêu đề hợp lệ, lưu vào "Title 0. Begin"
                types.append("Table")
                sessions.append("Title 0. Begin")
            continue

        # Xử lý ảnh (Image)
            # contents_image = [el for el in element if 'Image' in str(type(el))]
        if 'Image' in str(type(element)):
           contents_image.append(element)  # Lưu metadata của ảnh
           continue

        # Xử lý các loại text khác (NarrativeText, ListItem, etc.)
        content += element_str + "\n"

    # Lưu session cuối cùng nếu tồn tại
    if session and content:
        sessions.append(session)
        contents.append(content)
        types.append("Text")

    return sessions, contents, contents_image, types

while True:
    elements = partition_pdf(filename=filename,
                         strategy = "hi_res",
                         infer_table_structure=True,
                         model_name = 'yolox')
    session, text, image, types = check_session(elements)
    
    time.sleep(5)