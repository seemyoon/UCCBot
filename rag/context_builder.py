from vector_db import VectorDB


class ContextBuilder:
    def __init__(self):
        self.vectordb = VectorDB()

    def build(self, retrieved_chunks):
        if not retrieved_chunks:
            return ""

        all_context = []

        for chunk in retrieved_chunks:
            metadata = chunk.metadata

            if "article_num" in metadata:
                context = self._build_article_context(chunk)
            elif "section" in metadata and metadata.get("part") == "ПРИКІНЦЕВІ ТА ПЕРЕХІДНІ ПОЛОЖЕННЯ":
                context = self._build_section_context(chunk)
            elif "act_name" in metadata:
                context = chunk.page_content
            else:
                context = chunk.page_content

            all_context.append(context)

        return "\n".join(all_context).strip()

    def _build_article_context(self, chunk):
        metadata = chunk.metadata

        part_name = metadata["part"]
        section_name = metadata["section"]
        article_num = metadata["article_num"]

        if metadata.get("total_chunks", 1) == 1:
            return f"{part_name}. {section_name}. {chunk.page_content}"

        data = self.vectordb.vectordb._collection.get(
            where={"article_num": article_num}
        )

        documents = data["documents"]
        metadatas = data["metadatas"]

        sorted_chunks = sorted(
            zip(documents, metadatas),
            key=lambda x: x[1].get("chunk_index", 0)
        )

        result = " ".join(doc for doc, _ in sorted_chunks).strip()

        return f"{part_name}. {section_name}. {result}"

    def _build_section_context(self, chunk):
        metadata = chunk.metadata

        part_name = metadata["part"]
        section_name = metadata["section"]
        chunk_index = metadata.get("chunk_index", 0)
        total_chunks = metadata.get("total_chunks", 1)

        data = self.vectordb.vectordb._collection.get(
            where={
                "section": section_name,
                "part": part_name
            }
        )

        documents = data["documents"]
        metadatas = data["metadatas"]

        neighbor_indices = self._get_neighbor_indices(chunk_index, total_chunks)

        merged_docs = [
            (meta["chunk_index"], doc)
            for doc, meta in zip(documents, metadatas)
            if meta.get("chunk_index") in neighbor_indices
        ]

        merged_docs.sort(key=lambda x: x[0])
        result = " ".join(doc for _, doc in merged_docs).strip()

        return f"{part_name}. {section_name}. {result}"

    @staticmethod
    def _get_neighbor_indices(idx, total):

        neighbor_indices = []
        if idx is not None:
            neighbor_indices.append(idx)
            if idx - 1 >= 0:
                neighbor_indices.append(idx - 1)
            if idx + 1 < total:
                neighbor_indices.append(idx + 1)

        return sorted(set(neighbor_indices))
