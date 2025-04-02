from elasticsearch import Elasticsearch
import pandas as pd
es = Elasticsearch("http://localhost:9200",)
client = es.info()
print(client)
# ---------------------
from sentence_transformers import SentenceTransformer
model_embed = SentenceTransformer('all-mpnet-base-v2')
# ---------------------
from geneate_qa.classDocling import DoclingProcessor
from geneate_qa.classSummarize import SummarizeText
from geneate_qa.classDefineCT import VerilogProcessor
source = "E:\anaconda_set\VeronChatBot\geneate_qa\code.pdf" #Đường dẫn file
processor = DoclingProcessor(source)
sections = processor.process_document()
# ----------------------------------
refine = VerilogProcessor(model_id="gemma3:27b", host="http://192.168.1.19:11434")
refine_text = [refine.format_code(section).content for section in sections]  # Optimized to one line
# ----------------------------------
model_sum = SummarizeText(model_id="gemma3:27b", host="http://192.168.1.19:11434")
summary = [model_sum.generate_dataset(content) for content in refine_text]
# ----------------------------------
summary_embed = [model_embed.encode(content) for content in summary]
# ----------------------------------
Processed_data= []
for i in range(len(refine_text)):
    Processed_data.append({
        "content": refine_text[i],
        "summary": summary[i],
        "summary_embed": summary_embed[i]
    })
from indexMapping import indexMapping
index_name = 'data'
if es.indices.exists(index=index_name):
  es.indices.delete(index=index_name)
  print(f"Index '{index_name}' deleted.")
es.indices.create(index=index_name, mappings=indexMapping)
# --------
for item in Processed_data:
    try:
      es.index(index=index_name, document=item)
    except Exception as e:
        print(f"Error indexing document: {e}")
        print(f"Document content: {item}")
# ---
