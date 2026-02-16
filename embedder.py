from typing import List, Dict, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter
from tqdm import tqdm


class Embedder:
    def __init__(
            self,
            embedder,
            max_chunk_tokens: int,
            # chunk_overlap: int,
            law_name: str,
            source_file: str
    ):
        self.embedder = embedder
        self.max_chunk_tokens = max_chunk_tokens
        # self.chunk_overlap = chunk_overlap
        self.law_name = law_name
        self.source_file = source_file

    def embed_and_prepare_chunks(
            self,
            text: str,
            part: str,
            section_title: str,
            article_num: Optional[str] = None
    ) -> List[Dict]:
        # split text into chunks

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.max_chunk_tokens,
            # chunk_overlap=self.chunk_overlap,
            length_function=len  # length_function(text) → number
        )

        chunks = splitter.split_text(text)
        total_chunks = len(chunks)
        db_chunks = []

        for idx, chunk_text in enumerate(tqdm(chunks)):
            embedding = self.embedder.embed_query(chunk_text)

            metadata = {
                "part": part,
                "section": section_title,
                "law_name": self.law_name,
                "source_file": self.source_file,
                "chunk_index": idx,
                "total_chunks": total_chunks,
            }
            if article_num is not None:
                metadata["article_num"] = article_num

            db_chunks.append({
                "vector": embedding,
                "page_content": chunk_text,
                "metadata": metadata
            })

        return db_chunks

    def parse_main_structure(self, text, part_pattern, section_pattern, article_pattern) -> List[Dict]:

        db_entries = []

        for part_match in part_pattern.finditer(text):
            part_start = part_match.start()  # index
            part_text = part_match.group()

            # print('PART:', part_text)

            next_part = part_pattern.search(text, pos=part_start + 1)
            # pos= means start searching from character index N in the string
            # part_start + 1 - now the search starts after the first character of the current match, without '+1' will find the same match again.

            part_end = next_part.start() if next_part else len(text)
            # there is another part: end = start of next part. there is no next part: end = end of whole text

            for section_match in section_pattern.finditer(text, pos=part_start):
                section_start = section_match.start()

                if section_start >= part_end:  # if this section starts after the end of the current PART → stop
                    break

                section_title = section_match.group()
                # print('  SECTION:', section_title)

                next_section = section_pattern.search(text, pos=section_start + 1)
                section_end = min(
                    next_section.start() if next_section else len(text),
                    part_end
                )

                # it chooses the nearest wall.
                # [ Section Start ] ---- articles ---- [ Next Section OR Part End ]

                for article_match in article_pattern.finditer(text, pos=section_start):
                    article_start = article_match.start()

                    if article_start >= section_end:
                        break

                    article_num = article_match.group(1)
                    article_text = article_match.group(2)

                    full_article_text = (
                        f"Стаття {article_num}. {article_text}"
                    )

                    # print('    ARTICLE:', article_num, article_text)

                    db_entries.extend(
                        self.embed_and_prepare_chunks(
                            text=full_article_text,
                            part=part_text,
                            section_title=section_title,
                            article_num=article_num
                        )
                    )

        return db_entries

    def parse_additional_structure(self, text, part_pattern, section_pattern) -> List[Dict]:

        db_entries = []

        for part_match in part_pattern.finditer(text):
            part_start = part_match.start()
            part_text = part_match.group()

            next_part = part_pattern.search(text, pos=part_start + 1)
            part_end = next_part.start() if next_part else len(text)

            for section_match in section_pattern.finditer(text, pos=part_start):
                section_start = section_match.start()
                if section_start >= part_end:
                    break

                section_title = section_match.group(1)
                section_text = section_match.group(2)

                db_entries.extend(
                    self.embed_and_prepare_chunks(
                        text=section_text,
                        part=part_text,
                        section_title=section_title
                    )
                )

        return db_entries

    def embed_footer_part(self, footer_json: Dict) -> List[Dict]:

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.max_chunk_tokens,
            # chunk_overlap=self.chunk_overlap,
            length_function=len
        )
        chunks = splitter.split_text(footer_json['text'])
        total_chunks = len(chunks)
        db_chunks = []

        for idx, chunk_text in enumerate(tqdm(chunks)):
            embedding = self.embedder.embed_query(chunk_text)

            metadata = {
                "act_type": footer_json['act_type'],
                "act_name": footer_json['act_name'],
                "signed_by": footer_json['signed_by'],
                "number_and_date": footer_json['number_and_date'],
                "edition": footer_json['edition'],
                "status": footer_json['status'],
                "permanent_link": footer_json['permanent_link'],
                "chunk_index": idx,
                "total_chunks": total_chunks
            }

            db_chunks.append({
                "vector": embedding,
                "metadata": metadata,
                "page_content": chunk_text
            })

        return db_chunks
