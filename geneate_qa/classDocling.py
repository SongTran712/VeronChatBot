import re
from docling.document_converter import DocumentConverter

class DoclingProcessor:
    def __init__(self, source: str):
        self.source = source
        self.converter = DocumentConverter()
        self.result = self.converter.convert(self.source)
    
    def export_markdown(self) -> str:
        return self.result.document.export_to_markdown()
    
    def convert_section_tags(self, text: str) -> str:
        def replace_tag(match):
            tag, locs, title = match.groups()
            if re.match(r'\d+\.\d*', title.strip()):
                return match.group(0)  # Giữ nguyên nếu tiêu đề bắt đầu bằng số và dấu chấm
            return f'<text>{locs}{title}</text>'  # Thay thế bằng <text>
        
        pattern = re.compile(r'(<section_header_level_\d+>)(<.*?>)?([^<>]+)</section_header_level_\d+>', re.DOTALL)
        return pattern.sub(replace_tag, text)
    
    def extract_sections(self, text: str) -> list:
        sections = []
        current_section = None
        current_content = ""
        first_section = True  # Đánh dấu nếu chưa gặp tiêu đề nào
        
        lines = text.splitlines()
        
        for line in lines:
            # Xóa các thẻ <loc_*> khỏi dòng
            line = re.sub(r"<loc_\d+>", "", line).strip()
            
            # Nếu gặp tiêu đề mới
            if line.startswith("<section_header_level_1>"):
                # Nếu trước khi gặp tiêu đề đầu tiên đã có nội dung, lưu lại nó
                if first_section and current_content.strip():
                    sections.append(f"{current_content.strip()}")
                    current_content = ""
                
                first_section = False  # Đã gặp một tiêu đề
                
                # Lưu lại nội dung của section trước nếu có
                if current_section is not None:
                    sections.append(f"{current_section}\n{current_content.strip()}")
                
                # Lấy tiêu đề mới và reset nội dung
                current_section = re.sub(r"<.*?>", "", line)
                current_content = ""
            
            else:
                if line.startswith("<otsl>"):
                    current_content += "\n" + line.strip()
                elif line.startswith("<page_footer>") or line.startswith("<page_header>"):
                    continue
                else:
                    current_content += "\n" + re.sub(r"</?[^<>]+>", "", line).strip()
        
        # Lưu lại phần nội dung cuối cùng (nếu có)
        if current_content.strip():
            if current_section:
                sections.append(f"{current_section}\n{current_content.strip()}")
            else:
                sections.append(f"{current_content.strip()}")  # Nội dung không có tiêu đề nào
        
        return sections
    
    def process_document(self) -> list:
        data = self.result.document.export_to_doctags()
        processed_data = self.convert_section_tags(data)
        return self.extract_sections(processed_data)

# Example usage:
# processor = DoclingProcessor(source="/content/docs.pdf")
# sections = processor.process_document()
# print(sections)