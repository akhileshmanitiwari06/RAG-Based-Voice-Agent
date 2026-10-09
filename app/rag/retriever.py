import faiss
import numpy as np

from sentence_transformers import SentenceTransformer

from app.rag.metadata import load_templates


class RAGRetriever:

    def __init__(self):

        self.templates = load_templates()

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        documents = [
            self._build_document(template)
            for template in self.templates
        ]

        embeddings = self.model.encode(
            documents,
            normalize_embeddings=True,
        )

        embeddings = np.asarray(
            embeddings,
            dtype="float32",
        )

        self.index = faiss.IndexFlatIP(
            embeddings.shape[1]
        )

        self.index.add(embeddings)

    @staticmethod
    def _build_document(template):

        return " ".join(
            [
                template.get("template_id", ""),
                template.get("intent", ""),
                template.get("operation", ""),
                template.get("description", ""),
                template.get("verification", ""),
            ]
        )

    def search(
        self,
        query: str,
        top_k: int = 3,
    ):

        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
        )

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32",
        )

        scores, indices = self.index.search(
            query_embedding,
            min(top_k, len(self.templates)),
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):

            if index < 0:
                continue

            template = dict(
                self.templates[index]
            )

            template["score"] = float(score)

            results.append(template)

        return results


_retriever = None


def get_retriever():

    global _retriever

    if _retriever is None:
        _retriever = RAGRetriever()

    return _retriever


def search(
    query: str,
    top_k: int = 3,
):

    return get_retriever().search(
        query,
        top_k,
    )