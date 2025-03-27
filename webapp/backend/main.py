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
# from agno.tools.duckduckgo import DuckDuckGoTools
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
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.workflow import RunEvent, RunResponse, Workflow

from typing import Union, Literal, Dict

model = Ollama(id="llama3.2:1b", host="http://localhost:11434")
engine = create_engine("postgresql+psycopg2://ai:ai@localhost:5555/ai")
embed_model = SentenceTransformer('all-mpnet-base-v2')

class Base(DeclarativeBase):
    pass

class History(Base):
    __tablename__ = "history1234"
    id = Column(Integer, primary_key=True, autoincrement= True)
    user = Column(String, index = True)
    session = Column(String, index = True)
    input = Column(String)
    response = Column(String)
    # summarize = Column(String)
    # embedding = Column(Vector(768))
    
Base.metadata.create_all(bind=engine)

def get_summarize_agent(
) -> Agent:
    """Get an Agentic RAG Agent with Memory."""
    agentic_rag_agent: Agent = Agent(
        model = model,
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

def retrieve_history():
    # query_vector = embed_model.encode(prompt)
    try:
        with Session(engine) as session:
            outs = session.query(History).limit(3).all()
            results = ""
            if outs:
                for out in outs:
                    # info = out
                    
                    results += f"user : {out.input}\nassistant : {out.response}\n"
                
                summarize = summarize_agent.run(results).content
                print(summarize)
                return json.dumps({"Summarize":summarize}, indent= 2)
            return  None

    except Exception as e:
        print(e)
            
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
                "Type": source_data.get("Type"),
                "Session": source_data.get("Session"),
                "Content": source_data.get("Content"),
                # "Summary": source_data.get("Summary")
            })
        return json.dumps(results, indent=2)   
      

class SearchResults(BaseModel):
    output: Literal['Greeting', 'Question'] = Field(None, description="Simple Greeting or Question")
    # input x
    
def get_route_agent():
    agentic_rag_agent = Agent(
        model = model,
        description=["You are a helpful assistant, an expert at classifying whether the input is 'Greeting' or 'Question'."],
        instructions=dedent("""\
            Classify the input based on the following criteria:
            
            - Label as "Greeting" if the input is a common form of greeting (e.g., "Hello", "Hi", "Good morning", "How are you?").
            - Label as "Question" if the input is a direct question or inquiry, even if it doesn't start with a typical question word (e.g., "What is the capital of France?", "HaNoi is the capital of VietNam?").
            
            If the input contains both a greeting and a question (e.g., "Hi, where is Japan?"), prioritize classifying it as "Question" over "Greeting".
            
            For clarity:
            - "Greeting": Any phrase commonly used as a form of address or social greeting.
            - "Question": Any phrase that is asking for information or clarification, regardless of whether it contains a question mark.
        """), 
        response_model=SearchResults,
        structured_outputs = True
        # reasoning = True
    )
    return agentic_rag_agent

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

def get_greet_agent(
) -> Agent:
    agentic_rag_agent: Agent = Agent(
        # name="agentic_rag_agent",
        model=model,
        description = [
    "You are VERON, a helpful IC assistant. Your goal is to provide a formal, yet basic greeting response."
],

    context = {"history": retrieve_history()},

    instructions = dedent("""\
        - Maintain a formal but friendly tone for greetings.
        - Respond politely and professionally, ensuring warmth and respect.
        - Feel free to use the historical context to tailor your response if it's not empty: {history}.
        - Avoid casual language or overly informal expressions, unless the user indicates otherwise.
        - If appropriate, ask follow-up questions to continue the conversation smoothly.
    """),
            add_context = True,
            markdown = True
        
        )
    return agentic_rag_agent


def get_research_agent(
) -> Agent:
    """Get an Agentic RAG Agent with Memory."""
    agentic_rag_agent: Agent = Agent(
        # name="agentic_rag_agent",
        model=model,
        description = [
    "You are VERON, a helpful assistant. Your goal is to research and provide answers based on the available tools and information."
],

    instructions = dedent("""\
        - Initiate the 'retrieve_tool' to gather relevant information.
        - If the 'retrieve_tool' provides useful information, base your answer on that.
        - If no useful information is retrieved, use the 'duckduckgo_search' tool with the input query to find relevant details.
        - If appropriate, incorporate historical context from the conversation: {history}.
        - Focus on providing a direct answer, without mentioning the tools used or the process behind your decision.
    """),
        # "If the input is a standard formal Greeting, such as 'Hello' or 'How are you' or something like that just return None",
        tools=[RetrieveTools(), DuckDuckGoTools()],
        # markdown= True,
        # structured_outputs = True,
        add_context = True,
        context = {"history": retrieve_history()},
        
    )

    return agentic_rag_agent

async def data_stream(llm, content):
    run_response = await llm.arun(content, stream = True)
    try:
        store_data = ""
        async for response in run_response:
            if isinstance(response, RunResponse):
            #     # Extract the content from the RunResponse object
            
                response_content = response.content
                # print(response_content)
                store_data += response_content
                yield response_content
        try:
            with Session(engine) as session:
                ins = History(user = "id123", session = "id1", input = content
                        , response = store_data
                        # , embedding = embed_model.encode(f"input:{content} - response:{store_data}")
                        )
                session.add(ins)
                session.commit()
        except Exception as e:
            print(f"Caught exception: {e}")
    finally:
        print("Stream success")



@asynccontextmanager
async def lifespan(app: FastAPI):
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

@app.post("/api/chat")
async def ask(req: Item):
    route_out = await asyncio.to_thread(route_llm.run, req.content) 
    # route_out = route_llm.run(req.content).content.output
    if route_out.content.output == 'Greeting':
        llm_final = get_greet_agent()
        know_base = req.content
    else:
        llm_final = get_core_agent()
        know = route_out = await asyncio.to_thread(route_llm.run, req.content) 
        know_base = know.content
        
    generator = data_stream(llm_final, know_base)
    return StreamingResponse(generator, media_type="text/event-stream"
                        , headers={"cache-Control": "no-cache", "cf-cache-status": "DYNAMIC",
                                   "x-content-type-options": "nosniff", "content-type":"text/event-stream"}
                        )

if __name__ == "__main__":
    route_llm = get_route_agent()
    res_llm = get_research_agent()
    llm_final = get_core_agent()
    summarize_agent = get_summarize_agent()
    uvicorn.run(app, host="0.0.0.0", port=8000)