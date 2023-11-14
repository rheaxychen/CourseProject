import math

class BM25Ranker:
    def __init__(self, documents):
        self.documents = documents
        self.avg_doc_length = sum(len(doc) for doc in documents) / len(documents)
        self.k1 = 1.5  # Tuning parameter
        self.b = 0.75  # Tuning parameter

    def calculate_idf(self, term, documents):
        # Calculate inverse document frequency (IDF)
        doc_count_with_term = sum(1 for doc in documents if term in doc)
        return math.log((len(documents) - doc_count_with_term + 0.5) / (doc_count_with_term + 0.5) + 1.0)

    def calculate_bm25_score(self, query, document):
        score = 0.0
        for term in query:
            term_freq_in_doc = document.count(term)
            idf = self.calculate_idf(term, self.documents)
            numerator = term_freq_in_doc * (self.k1 + 1.0)
            denominator = term_freq_in_doc + self.k1 * (1.0 - self.b + self.b * len(document) / self.avg_doc_length)
            score += idf * numerator / denominator
        return score

    def rank_documents(self, query):
        # Rank documents based on BM25 score
        scores = [(index, self.calculate_bm25_score(query, document)) for index, document in enumerate(self.documents)]
        ranked_documents = sorted(scores, key=lambda x: x[1], reverse=True)
        return ranked_documents