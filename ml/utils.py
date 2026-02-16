from pypdf import PdfReader


class Utils:
    @staticmethod
    def load_pdf_text(path: str) -> str:

        reader = PdfReader(path)
        pages = []

        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)

        return '\n'.join(pages)
