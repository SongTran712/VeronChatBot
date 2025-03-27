import asyncio
from typing import List
import json
from agno.agent import Agent
from agno.models.ollama import Ollama
from pydantic import BaseModel, Field
from textwrap import dedent
from agno.tools import Toolkit
from elasticsearch import Elasticsearch
from typing import Optional
from sentence_transformers import SentenceTransformer
embed_model = SentenceTransformer('all-mpnet-base-v2')

class AnswerQuestion(BaseModel):
    session_id: str = Field(..., description="A concise yet meaningful identifier for the session related to the provided 'Knowledge_Base'. Ensure it remains general and descriptive.")

    question: str = Field(..., description="Generate three well-formed questions that directly relate to the concepts, rules, or explanations provided in the 'Knowledge_Base'. The questions should encourage in-depth understanding. ")

    answer: str = Field(..., description="Provide three accurate and contextually relevant answers based on the 'Knowledge_Base', ensuring they directly correspond to the generated questions.")
class RetrieveTools(Toolkit):
    def __init__(
        self,
    ):
        super().__init__(name = "retrieve_tools")
        self.es = Elasticsearch(
    "http://localhost:9200",
)
        self.register(self.retrieve_tool)
    def retrieve_tool(self, prompt:str) -> Optional[str]:
        if self.es.ping():
            print('Connected to ES!')
        else:
            print('Could not connect to ES!')
            exit(1)
        max_candi = self.es.count(index="rag")["count"]
        if max_candi > 0:
            query = {
            "field" : "SummaryVector",
            "query_vector" : embed_model.encode(prompt),
            "k" : 5,
            "num_candidates" : max_candi , 
        }
        res = self.es.knn_search(index="rag", knn=query , source=["Type","Session","Content","Summary"])
        results = []

        for hit in res['hits']['hits']:
            if hit['_score'] < 0.5:
                continue
            source_data = hit['_source']
            # print(source_data.get("Content"))
            results.append({
                "Content":  """Gaeng Som Phak Ruam
                        Sour Curry with Mixed Vegetables
                1. Clean the shrimps thoroughly and devein
                them. Bring the vegetable stock (or water) to a boil and
                add Gaeng Som paste. 2. When the soup returns to a full
                boil, add vegetables in this order: cauliflower, long beans
                and cabbage. 3. Season with palm sugar, tamarind juice
                and fish sauce, making sure everything is well dissolved.
                4. Add shrimps and cook briefly.
                Tips: • As an alternative, shrimp can be replaced with fish.
                • Seafood cooks quite quickly thus shrimp and fish
                should be in the boiling soup only briefly, and
                then whisked out and served to keep it fresh
                and juicy.
                • Prepare the drier, tougher ingredients first, like
                cauliflower and long beans, followed by leafy
                vegetables like cabbage.
""",       
            })
        return json.dumps(results, indent=2)   
      
structured_output_agent = Agent(
    model=Ollama(id="llama3.2:1b"),
    description= dedent("""\
        You are an expert in generating high-quality question-answer (QA) pairs, designed to enhance comprehension and knowledge retention.  
        Your strength lies in crafting precise, contextually relevant questions and well-structured answers that cater to various difficulty levels.  You use 'Tools' to get the Knowledge_base
        You ensure that each QA pair is clear, informative, and aligned with the given content.\
    """),
    instructions=dedent("""\
        When generating QA pairs, follow these principles:  

        1. Ensure clarity and relevance:  
           - Questions should be direct, unambiguous, and closely related to the provided content.  
           - Answers should be concise, accurate, and provide meaningful insights.  

        2. Vary difficulty levels:  
           - Create a mix of basic, intermediate, and advanced questions to suit different audiences.  

        3. Maintain structure and coherence:  
           - Each QA pair should be well-formed, avoiding redundancy or unnecessary complexity.  

        4. Adapt to the content type:  
           - For factual topics, focus on objective and knowledge-based questions.  
           - For conceptual topics, include thought-provoking or explanatory questions.\
    """),
    response_model= AnswerQuestion,
    tools = [RetrieveTools()]
)
from agno.run.response import RunResponse
from rich.pretty import pprint
# Run the agent synchronously
structured_output_response: RunResponse = structured_output_agent.run("a Thai dish")
pprint(structured_output_response.content)

    