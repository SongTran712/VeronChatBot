from agno.agent import Agent
from agno.models.ollama import Ollama
from pydantic import BaseModel, Field
from textwrap import dedent
content = "abcdefgh"   #Ví dụ nội dung input là "abcdefgh"
class AnswerQuestion(BaseModel):
    # session_id: str = Field(..., description="A concise yet meaningful identifier for the session related to the provided 'Knowledge_Base'. Ensure it remains general and descriptive.")

    question: str = Field(...)

    answer: str = Field(...)

class ThreeAQ(BaseModel):
    aqlist: list[AnswerQuestion]
      
from agno.run.response import RunResponse
from rich.pretty import pprint
# Run the agent synchronously
import pandas as pd
def generate_dataset(data, content):
    structured_output_agent = Agent(
    model=Ollama(id="llama3.2:1b"),
    description= dedent("""\
        You are an expert in generating high-quality question-answer (QA) pairs to build dataset, designed to enhance comprehension for major study and research topic.  
        Your strength lies in crafting precise, contextually relevant questions and well-structured answers that cater to various difficulty levels. 
        You ensure that each QA pair is clear, informative, and aligned with the given content.
        MAKE SURE YOU GENERATE AT LEAST THREE PAIR QA-PAIRS !!!\
    """),
    instructions=dedent("""\
        When generating THREE QA pairs, follow these principles:  

        1. Ensure clarity and relevance:  
           - Questions should be direct, unambiguous, and closely related to the provided content.  
           - Answers should be concise, accurate, and provide meaningful insights.  

        2. Vary difficulty levels:  
           - Create a mix of basic, intermediate, and advanced questions to suit different audiences.  

        3. Maintain structure and coherence:  
           - Each QA pair should be well-formed, avoiding redundancy or unnecessary complexity.  

        4. Adapt to the content type:  
           - For factual topics, focus on objective and knowledge-based questions.  
           - For conceptual topics, include thought-provoking or explanatory questions.
           - For the research topics or major, try to think and answer more depth and give the detail answer.\
    """),
    response_model= ThreeAQ,
    structured_outputs= True,
    )
    structured_output_response: RunResponse = structured_output_agent.run(content)
    QAstack = structured_output_response.content
    for i in range(len(QAstack.aqlist)):
        ques = QAstack.aqlist[i].question
        ans = QAstack.aqlist[i].answer
        data.append({"question": ques, "answer": ans})
    return data
data = []
# Create a DataFrame from the list
df = pd.DataFrame(generate_dataset(data, content))
''' NOTE: content được lấy từ Retrieve nội dung !!!'''
