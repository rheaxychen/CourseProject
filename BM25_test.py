import unittest
from BM25 import BM25Ranker
class TestBM25Ranker(unittest.TestCase):
    def setUp(self):
        # Set up some sample documents for testing
        self.documents = [
            ["apple", "banana", "kiwi"],
            ["apple", "banana", "grape"],
            ["orange", "grape", "kiwi"],
            ["banana", "kiwi", "melon"],
        ]
        self.bm25_ranker = BM25Ranker(self.documents)

    def test_calculate_idf(self):
        # Test the calculate_idf method
        self.assertAlmostEqual(self.bm25_ranker.calculate_idf("apple", self.documents), 0.6931, places=4)
        self.assertAlmostEqual(self.bm25_ranker.calculate_idf("kiwi", self.documents), 0.3567, places=4)

    def test_calculate_bm25_score(self):
        # Test the calculate_bm25_score method
        query = ["apple", "banana"]
        document = ["apple", "banana", "orange"]
        score = self.bm25_ranker.calculate_bm25_score(query, document)
        self.assertAlmostEqual(score, 1.0498, places=4)

    def test_rank_documents(self):
        # Test the rank_documents method
        query = ["apple", "banana"]
        ranked_documents = self.bm25_ranker.rank_documents(query)
        self.assertEqual(ranked_documents, [(0, 1.0498221244986776), (1, 1.0498221244986776), (3, 0.3566749439387324), (2, 0.0)])

if __name__ == '__main__':
    unittest.main()
