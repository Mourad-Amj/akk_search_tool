# Streamlit proof of concept
# ----------------------------------------------------------------
#### ATTENTION ####
# ----------------------------------------------------------------
# FAISS needs to be installed in a conda environment
# Install all the other dependencies inside the conda environment using pip install
# ----------------------------------------------------------------
# Run this with 
# python -m streamlit run proof_of_concept/app.py --server.headless true
# ----------------------------------------------------------------

# imports
import streamlit as st
import pandas as pd
import io
import xlsxwriter

from sentence_transformers import SentenceTransformer, util
import datetime


import faiss        # Similarity search function
import numpy as np  # Similarity search function

# ---------------------------------------------------------------- Similarity search function
def perform_similarity_search(database, search_text, embedder):
    # Create an embedding for the search text
    search_vector = embedder.encode(search_text, convert_to_tensor=False)
    _vector = np.array([search_vector])
    faiss.normalize_L2(_vector)

    # Create a matrix of embeddings for the database
    vectors = np.array([item['embedding'] for item in database])
    faiss.normalize_L2(vectors)

    # Initialize FAISS index
    vector_dimension = vectors.shape[1]
    index = faiss.IndexFlatL2(vector_dimension)
    index.add(vectors)

    # Perform similarity search
    k = index.ntotal
    distances, ann = index.search(_vector, k=k)

    # Create a DataFrame to store search results
    results = pd.DataFrame({'distances': distances[0], 'ann': ann[0]})

    # Merge results with the database
    merge = pd.merge(results, pd.DataFrame(database), left_on='ann', right_index=True)

    # Retrieve category label from the merged DataFrame
    labels = merge['category']
    category = labels[ann[0][0]]
    return category


# Use the perform_similarity_search function here
similarity_category = perform_similarity_search(agenda_search, search, embedder)

# ---------------------------------------------------------------- End of similarity_search