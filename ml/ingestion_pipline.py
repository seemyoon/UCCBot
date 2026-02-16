import config
from ml.embedder import Embedder
from preprocessing.openai_chat_processor import OpenAIChatProcessor
from preprocessing.legal_text_patterns import LegalTextPatterns
from preprocessing.text_normalizer import TextNormalizer
from preprocessing.text_processor import TextProcessor
from ml.utils import Utils
from vector_db import VectorDB


class IngestionPipeline:

    def __init__(self):
        self.embedder = Embedder(
            embedder=config.EMBEDDER,
            max_chunk_tokens=config.MAX_CHUNKS_TOKENS,
            # chunk_overlap=config.CHUNK_OVERLAP,
            law_name=config.LAW_NAME,
            source_file=config.CRIMINAL_CODE_DOC
        )
        self.source_file = config.CRIMINAL_CODE_DOC
        self.utils = Utils()
        self.text_processor = TextProcessor()
        self.text_normalizer = TextNormalizer()
        self.legal_text_patterns = LegalTextPatterns()
        self.openAI_chat_processor = OpenAIChatProcessor()
        self.vectorDB = VectorDB()

    def process_pdf(self):
        print("Step 1: Loading PDF text...")
        raw_text = self.utils.load_pdf_text(self.source_file)
        print("PDF loaded, number of characters:", len(raw_text))

        print("Step 2: Removing header...")
        raw_no_header = self.text_processor.remove_header(raw_text)
        print("Header removed.")

        print("Step 3: Splitting main text and footer...")
        main_text, footer_text = self.text_processor.split_main_and_footer(raw_no_header)
        print(f"Main text length: {len(main_text)}, Footer text length: {len(footer_text)}")

        print("Step 4: Splitting main text into two parts...")
        first_part, second_part = self.text_processor.split_main_into_2_parts(main_text)
        print(f"First part length: {len(first_part)}, Second part length: {len(second_part)}")

        print("Step 5: Processing footer text with OpenAI...")
        reformulate_footer_txt = self.openAI_chat_processor.process_footer_text(footer_text)
        print("Footer processed and structured.")

        print("Step 6: Normalizing first part of main text...")
        norm_first_part = self.text_normalizer.enforce_headings(
            self.text_normalizer.fix_line_breaks(
                self.text_normalizer.normalize_apostrophes(first_part)
            )
        )
        print("Step 6.1: Adding last fake article because the pattern cut the last article...")
        norm_first_part += "\nСтаття 999. Кінець документа"
        print("First part normalized.")

        print("Step 7: Normalizing second part of main text...")
        norm_second_part = self.text_normalizer.enforce_headings(
            self.text_normalizer.fix_line_breaks(
                self.text_normalizer.normalize_apostrophes(second_part)
            )
        )
        print("Second part normalized.")

        print("Step 8: Parsing main structure and generating embeddings...")
        main_entries = self.embedder.parse_main_structure(
            norm_first_part,
            self.legal_text_patterns.PART_PATTERN,
            self.legal_text_patterns.SECTION_PATTERN_MAIN_PART,
            self.legal_text_patterns.ARTICLE_PATTERN_MAIN_PART
        )
        print(f"Main structure processed, {len(main_entries)} chunks generated.")

        print("Step 9: Parsing additional structure and generating embeddings...")
        additional_entries = self.embedder.parse_additional_structure(
            norm_second_part,
            self.legal_text_patterns.PART_PATTERN,
            self.legal_text_patterns.SECTION_PATTERN_ADDITIONAL_PART
        )
        print(f"Additional structure processed, {len(additional_entries)} chunks generated.")

        print("Step 10: Embedding footer part...")
        footer_entries = self.embedder.embed_footer_part(reformulate_footer_txt)
        print(f"Footer structure processed, {len(footer_entries)} chunks generated.")

        print("Step 11: Uploading main entries to VectorDB...")
        self.vectorDB.upload_data(main_entries)
        print("Main entries uploaded.")

        print("Step 12: Uploading additional entries to VectorDB...")
        self.vectorDB.upload_data(additional_entries)
        print("Additional entries uploaded.")

        print("Step 13: Uploading footer entries to VectorDB...")
        self.vectorDB.upload_data(footer_entries)
        print("Footer entries uploaded.")

        print("Pipeline completed successfully!")


if __name__ == '__main__':
    pipline = IngestionPipeline()
    pipline.process_pdf()
