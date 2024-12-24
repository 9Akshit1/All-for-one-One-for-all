import sys
import json
import ast
import subprocess
import os
import nltk
nltk.download('stopwords')
nltk.download('punkt_tab')

# There were some issues with different OpenMP, so the following two lines bypass them.
# os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"    
# os.environ["OMP_NUM_THREADS"] = "1"
 
import fitz  # PyMuPDF
import spacy
from typing import List, Dict
import logging
import re
import numpy as np
import faiss  # Local vector database

try:
    from rake_nltk import Rake
except ModuleNotFoundError:
    print("rake_nltk module not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rake_nltk"])
    from rake_nltk import Rake

from transformers import AutoTokenizer, AutoModel
from sklearn.model_selection import train_test_split
import torch

from application_writer.generate import Generate_Main

nlp = spacy.load('en_core_web_md')

class AdvancedDocumentQA:
    def __init__(self, index_name):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/paraphrase-MiniLM-L6-v2")
        self.model = AutoModel.from_pretrained("sentence-transformers/paraphrase-MiniLM-L6-v2")

        self.dimension = self.model.config.hidden_size
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = {}
        self.index_name = index_name
        self.logger.info(f"FAISS index {index_name} initialized with dimension {self.dimension}")

    def preprocess_text(self, text: str) -> str:      
        doc = nlp(text)
        clean_text = " ".join([token.lemma_.lower() for token in doc if not token.is_stop and token.is_alpha])
        return clean_text

    def extract_text_from_file(self, file_path: str) -> str:
        try:
            if file_path.lower().endswith('.pdf'):
                with fitz.open(file_path) as pdf:
                    text = " ".join([page.get_text() for page in pdf])
                    return self.preprocess_text(text)
            elif file_path.lower().endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
                    return self.preprocess_text(text)
            else:
                self.logger.warning(f"Unsupported file type: {file_path}")
                return ""
        except Exception as e:
            self.logger.error(f"Text extraction error for {file_path}: {e}")
            return ""

    def chunk_text(self, text: str, chunk_size: int = 400, overlap: int = 50) -> List[str]:
        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunks.append(text[i:i + chunk_size])
        return chunks

    def embed_text(self, text: str) -> np.ndarray:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).numpy()

    def extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        rake = Rake()
        rake.extract_keywords_from_text(text)
        return rake.get_ranked_phrases()[:top_n]

    def weighted_score(self, query: str, text_chunk: str) -> float:
        query_keywords = set(self.extract_keywords(query))
        text_keywords = set(self.extract_keywords(text_chunk))
        keyword_overlap = len(query_keywords & text_keywords) / len(query_keywords | text_keywords)

        query_embedding = self.embed_text(query).flatten() 
        text_embedding = self.embed_text(text_chunk).flatten()  
        semantic_similarity = np.dot(query_embedding, text_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(text_embedding))

        return 0.7 * semantic_similarity + 0.3 * keyword_overlap

    def process_document(self, file_path: str):
        text = self.extract_text_from_file(file_path)
        chunks = self.chunk_text(text)
        embeddings = [self.embed_text(chunk) for chunk in chunks]

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            vector_id = f"{file_path}_{i}"
            self.metadata[vector_id] = {"text": chunk, "source": file_path}
            self.index.add(np.array(embedding))

        self.logger.info(f"Processed {file_path}: {len(chunks)} chunks")

    def query_and_extract_info(self, question: str, top_k: int = 5) -> Dict:
        query_embedding = self.embed_text(question).reshape(1, -1)
        distances, indices = self.index.search(query_embedding, top_k)
        results = []

        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.metadata):
                vector_id = list(self.metadata.keys())[idx]
                text_chunk = self.metadata[vector_id]["text"]
                score = self.weighted_score(question, text_chunk)
                results.append({
                    "text": text_chunk,
                    "source": self.metadata[vector_id]["source"],
                    "score": score
                })

        results = sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]
        return {"query": question, "results": results}

    def fine_tune_model(self, dataset_path: str):
        # Example placeholder for fine-tuning if labeled data is available
        pass

def main():
    INDEX_NAME = 'advanced-document-qa'
    input_data = sys.stdin.read()

    try:
        data = ast.literal_eval(input_data)
    except Exception as e:
        print(f"Input parsing error: {e}")
        return

    uploaded_files = data.get("uploaded_files", [])
    questions = data.get("questions", "").split('\n')

    try:
        qa_system = AdvancedDocumentQA(INDEX_NAME)

        for file_path in uploaded_files:
            qa_system.process_document(file_path)

        all_extracted_info = []

        for question in questions:
            if question.strip():
                results = qa_system.query_and_extract_info(question)
                all_extracted_info.append(results)
                print(f"Question: {question}")

        

        #print(all_extracted_info)
        Generate_Main(all_extracted_info)

    except Exception as e:
        print(f"Error: {e}")


main()