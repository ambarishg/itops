import numpy as np
from concurrent.futures import ThreadPoolExecutor
from sentence_transformers import SentenceTransformer

class EmbeddingGenerator:
    def __init__(self, 
                 embedding_model_name):
        self.embedding_model_name = embedding_model_name

    def get_embedding_query_vector(self,query):
        """Get the vector of the query

        Args:
            query (string): user input

        Returns:
            _type_: vector of the query
        """
        model = SentenceTransformer(self.embedding_model_name)
        query_vector = model.encode(query)
        return query_vector

    def generate_embedding_dataset(self, 
                                   df,
                                   content_column_name = "themes",
                                   embedding_column_name = "embeddings"):
        embedding_list = []

        def embed_row(row):
            content = row[content_column_name]
            embedding = self.get_embedding_query_vector(content)
            print(f"Completed EMBEDDING for ROW: {row.name + 1}")  # row.name gives the index
            return np.array(embedding)

        # Use ThreadPoolExecutor for I/O bound tasks or ProcessPoolExecutor for CPU bound tasks
        with ThreadPoolExecutor() as executor:
            embedding_list = list(executor.map(embed_row, [df.iloc[i] for i in range(len(df))]))

        df[embedding_column_name] = embedding_list
        return df
