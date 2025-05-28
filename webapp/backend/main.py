from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
# import asyncio
import uvicorn
from pydantic import BaseModel, Field
# from langchain_ollama import ChatOllama
# from langchain.callbacks import AsyncIteratorCallbackHandler
# from langchain.schema import HumanMessage
from contextlib import asynccontextmanager
from kafka_producer import send_stream_of_messages
# from kafka_delete import delete_all_kafka_topics
from kafka_consumer import consume_tokens_from_kafka
import uuid
# from elasticsearch import Elasticsearch
from agno.agent import Agent, RunResponse
from agno.models.ollama import Ollama
import asyncio 
from typing import Iterator, AsyncIterator
from textwrap import dedent
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import asyncio
from agno.tools import Toolkit
from agno.tools.duckduckgo import DuckDuckGoTools
# from agno.knowledge.pdf import PDFKnowledgeBase
# from agno.vectordb.pgvector import PgVector
# from agno.embedder.ollama import OllamaEmbedder
# from agno.document.base import Document
# from agno.knowledge.document import DocumentKnowledgeBase
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Column, Integer, String
from pgvector.sqlalchemy import Vector
from sqlalchemy import select
from typing import Optional
from agno.workflow import RunEvent, RunResponse, Workflow
from agno.tools.email import EmailTools
from typing import Union, Literal
from duckduckgo_search import DDGS
<<<<<<< HEAD

model = Ollama(id="llama3.2:1b", host="http://192.168.30.172:11434")
=======
    
model = Ollama(id="qwen3:4b", host="http://localhost:11434")
>>>>>>> 9452253ba450af6470b7f736301fc0652ba22eed
engine = create_engine("postgresql+psycopg2://ai:ai@localhost:5555/ai")
embed_model = SentenceTransformer('all-mpnet-base-v2')

class Base(DeclarativeBase):
    pass

# class History(Base):
#     __tablename__ = "history1234"
#     id = Column(Integer, primary_key=True, autoincrement= True)
#     user = Column(String, index = True)
#     sessionID = Column(String, index = True)
#     input = Column(String)
#     response = Column(String)
    # summarize = Column(String)
    # embedding = Column(Vector(768))
    
Base.metadata.create_all(bind=engine)

def get_summarize_agent(
) -> Agent:
    """Get an Agentic RAG Agent with Memory."""
    agentic_rag_agent: Agent = Agent(
<<<<<<< HEAD
        model = Ollama(id="llama3.2:1b", host="http://192.168.30.172:11434"),
=======
        model = Ollama(id="llama3.2:3b", host="http://localhost:11434"),
>>>>>>> 9452253ba450af6470b7f736301fc0652ba22eed
        # name="agentic_rag_agent",
        description = [
    "This task involves creating a clear and concise summary of the conversation. Capture the key points, main takeaways, and any user requests or assistant responses, ensuring the summary is under 100 words."
],

        instructions = dedent("""\
            Provide a brief summary of the chat history, focusing on the main points discussed, key requests from the user, and relevant responses from the assistant. The summary should be concise, under 100 words, and exclude trivial details or repetition. Prioritize clarity and the essential context.
        """),
        # add_context = True,
    )
    return agentic_rag_agent



            
class RetrieveTools(Toolkit):
    def __init__(
        self,
    ):
        super().__init__(name = "retrieve_tools")
        self.es = Elasticsearch(
    "http://localhost:9200",
)
        self.register(self.elasticsearch)
        self.register(self.duckduckgo_search)
    def elasticsearch(self, prompt: str) -> Optional[str]:
        max_candi = self.es.count(index="rag")["count"]
        if max_candi == 0:
            return None

        try:
            vector = embed_model.encode(prompt)
        except Exception as e:
            print(f"Embedding failed: {e}")
            return None

        query = {
            "field" : "SummaryVector",
            "query_vector" : vector,
            "k" : 3,
            "num_candidates" : max_candi , 
            # "min_score": 0.4
        }

        try:
            res = self.es.knn_search(index="rag", knn=query , source=["text"])
        except Exception as e:
            print(f"Elasticsearch query failed: {e}")
            return None

        results = []
        for hit in res['hits']['hits']:
            # If you want to filter by score
            if hit['_score'] < 0.45:
                print(f"Low score: {hit['_score']}")
                continue

            text = hit['_source'].get("text")
            
            # Ensure the value is not a set (convert if needed)
            if isinstance(text, set):
                raise TypeError(f'Object of type set is not JSON serializable: {text}')

            results.append({"body": text})

        return json.dumps(results, indent=2) if results else None
    
    def duckduckgo_search(self, query: str, max_results: int = 5) -> str:
        actual_max_results = max_results
        search_query = query

        ddgs = DDGS(
        )
        return json.dumps(ddgs.text(keywords=search_query, max_results=actual_max_results), indent=2)


<<<<<<< HEAD
class SearchResults(BaseModel):
    output: Literal['Greeting', 'Question', 'Mail'] = Field(
        None, description="Simple Greeting, Question, or intent to Send Mail"
    )

def get_route_agent():
    agentic_rag_agent = Agent(
        model=Ollama(id="llama3.2:1b", host="http://192.168.30.172:11434"),
        description=["You are a helpful assistant, an expert at classifying whether the input is a 'Greeting', 'Question', or 'Mail' intent."],
=======
def get_greet_agent(user, session) -> Agent:
    agentic_rag_agent: Agent = Agent(
        model=model,
        description=[
            "You are VERON, a helpful IC assistant. Your goal is to provide formal yet clear and concise responses."
        ],
>>>>>>> 9452253ba450af6470b7f736301fc0652ba22eed
        instructions=dedent("""\
            - If the input is a greeting, respond with a formal and polite greeting.
            - If the input is a question, search for relevant information using Elasticsearch.
            - If Elasticsearch does not return useful results, fallback to DuckDuckGo search.
            - Answer the question based on the most relevant retrieved information.
        """),
        tools=[RetrieveTools()],
        markdown=True
    )
    return agentic_rag_agent

<<<<<<< HEAD
async def get_mail_agent():
    receiver_email = "songco712@gmail.com"
    sender_email = "Kieuphuongkai@gmail.com"
    sender_name = "PHƯƠNG"
    sender_passkey = "kqdifulobednqhym"
   
    mail_agent = Agent(
    model=Ollama(id="llama3.2:1b", host="http://192.168.30.172:11434"),
    tools=[
        EmailTools(
            receiver_email=receiver_email,
            sender_email=sender_email,
            sender_name=sender_name,
            sender_passkey=sender_passkey,
        )
    ]
)
    return mail_agent

def get_core_agent(
) -> Agent:
    """Get an Agentic RAG Agent with Memory."""
    agentic_rag_agent: Agent = Agent(
        # name="agentic_rag_agent",
        model=model,
        description = [
    "You are VERON, a helpful IC assistant. Your goal is to provide clear, engaging, and informative responses based on the given information."
],

    instructions = dedent("""\
        - Craft compelling and engaging introductions to capture attention.
        - Balance expertise with accessibility, ensuring clarity for all users.
        - Use clear, concise language and structure responses for easy scanning.
        - Include shareable takeaways to enhance the value of your response.
        - Organize responses with proper markdown for readability and structure.
    """),
        # add_context = True,
    )
    return agentic_rag_agent

async def get_greet_agent(
    user, session
) -> Agent:
    agentic_rag_agent: Agent = Agent(
        # name="agentic_rag_agent",
        model=model,
        description = [
    "You are VERON, a helpful IC assistant. Your goal is to provide a formal, yet basic greeting response."
],

    # context = {"history": await retrieve_history(user, session)},

    instructions = dedent("""\
        - Maintain a formal but friendly tone for greetings.
        - Respond politely and professionally, ensuring warmth and respect.
        
        - Avoid casual language or overly informal expressions, unless the user indicates otherwise.
        - If appropriate, ask follow-up questions to continue the conversation smoothly.
    """),
            # add_context = True,
            markdown = True
        # - Feel free to use the historical context to tailor your response if it's not empty: {history}.
        )
    return agentic_rag_agent

=======
>>>>>>> 9452253ba450af6470b7f736301fc0652ba22eed

from textwrap import dedent

async def get_research_agent(user, session) -> Agent:
    """Get an Agentic RAG Agent with Memory."""

    agentic_rag_agent: Agent = Agent(
<<<<<<< HEAD
        model=Ollama(id="llama3.2:1b", host="http://192.168.30.172:11434"),
=======
        model=Ollama(id="llama3.2:3b", host="http://localhost:11434"),
>>>>>>> 9452253ba450af6470b7f736301fc0652ba22eed

        description=[
            "You are VERON, a helpful assistant. Your goal is to research and provide answers based on the available tools and information."
        ],

        instructions=dedent("""\
        - Initiate the 'retrieve_tool' to gather relevant information.
        - If the 'retrieve_tool' provides useful information, base your answer on that and mention that you used the retrieve tool.
        - If no useful information is retrieved, use the 'duckduckgo' tool to find relevant details and state that you used DuckDuckGo.
        - You are allowed to mention the tool you used if it adds clarity or transparency to your answer.
        - Focus on providing a direct, useful response. Only mention the tool if it’s relevant or the user might benefit from knowing.
        """),

        tools=[RetrieveTools(), DuckDuckGoTools()],
        # add_context=True,
        markdown=True,
    )
    return agentic_rag_agent

async def data_stream(llm, content, user, sessionID):
    run_response = await llm.arun(content, stream = True)
    try:
        # store_data = ""
        async for response in run_response:
            if isinstance(response, RunResponse):
            #     # Extract the content from the RunResponse object
            
                response_content = response.content
                # print(response_content)
                # store_data += response_content
                if response_content is not None:
                    # print(response_content)
                    yield response_content
        # try:
        #     with Session(engine) as session:
        #         ins = History(user = user, sessionID = sessionID, input = content
        #                 , response = store_data
        #                 # , embedding = embed_model.encode(f"input:{content} - response:{store_data}")
        #                 )
        #         session.add(ins)
        #         session.commit()
        # except Exception as e:
        #     print(f"Caught exception: {e}")
    finally:
        print("Stream success")



@asynccontextmanager
async def lifespan(app: FastAPI):
    # route_llm.run("Hello")
    print("Starting FastAPI application...")
    yield  # FastAPI runs here

  
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class Item(BaseModel):
    content: str = Field(...)
    user: str = Field(...)
    sessionID: str = Field(...)
    
    
@app.post("/api/chat")
async def ask(req: Item):
    # route_out = await asyncio.to_thread(route_llm.run, req.content) 
    # print(req.user, req.sessionID)
    # # route_out = route_llm.run(req.content).content.output
    # if route_out.content.output == 'Greeting':
    #     llm_final = await get_greet_agent(req.user, req.sessionID)
    #     know_base = req.content
    # elif route_out.content.output == 'Mail':
    #     know_base = req.content
    #     llm_final = await get_mail_agent()
    # else:
    #     llm_final = get_core_agent()
    #     res_llm = await get_research_agent(req.user, req.sessionID)
    #     know = await asyncio.to_thread(res_llm.run, req.content) 
    #     know_base = know.content
    llm_final = get_greet_agent(req.user, req.sessionID)
    
    know_base = req.content
    generator = data_stream(llm_final, know_base, req.user, req.sessionID)
    return StreamingResponse(
            generator,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Content-Type-Options": "nosniff",
            })

if __name__ == "__main__":
    # route_llm = get_route_agent()
    summarize_agent = get_summarize_agent()
    uvicorn.run(app, host="0.0.0.0", port=8000)