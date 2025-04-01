from agno.agent import Agent
from agno.models.ollama import Ollama
from pydantic import BaseModel, Field
from textwrap import dedent
content = str(df['text'][14])  #Ví dụ nội dung input là "abcdefgh"
class AnswerQuestion(BaseModel):
    # session_id: str = Field(..., description="A concise yet meaningful identifier for the session related to the provided 'Knowledge_Base'. Ensure it remains general and descriptive.")
#helo
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
    model=Ollama(id="gemma3:27b", host="http://192.168.1.19:11434"),
    description = dedent("""\
    You are an expert in generating high-quality question-answer (QA) pairs to build datasets that enhance comprehension for major study and research topics.  
    Your strength lies in crafting precise, contextually relevant questions and well-structured answers that cater to various difficulty levels.  
    You ensure that each QA pair is clear, informative, and aligned with the provided content.  

    MAKE SURE YOU GENERATE AT LEAST THREE QA-PAIRS, AND IF THE CONTENT CONTAINS CODE, INCLUDE QUESTIONS SPECIFICALLY RELATED TO THE CODE.
"""),
    instructions = dedent("""\
    When generating THREE QA pairs, follow these principles:

    1. Ensure clarity and relevance:
       - Questions should be direct, unambiguous, and closely related to the provided content.
       - Answers should be concise, accurate, and provide meaningful insights.
       - If the content includes descriptive code snippets, ask questions about the code’s structure, syntax, functionality, and best practices.

    ***Example 1:***  
    **Input:**  
    ```  
    The format for module instantiation is:  
        - Comments must have the same indentation level as the section of code they refer to.  
        - Begin and End have the same indentation as the code they enclose.  

        ## Case Statement Format  
        case (signal3)  
            pvalue1:  
                begin  
                end  
            pvalue2, pvalue3, pvalue4:  
                begin  
                end  
            default:  
                begin  
                end  
        endcase  

        ## The format for the `always` and `initial` statements is:  
        always @(posedge clk19 or negedge rst_)  
            begin  
            if (!rst_)  
                begin  
                end  
            else  
                begin  
                if ()  
                    begin  
                    end  
                end  
        initial  
            begin  
            ...  
            end  

        ## The format for module instantiation is:  
        core icore // in case of instantiating a user-defined module  
            (  
            .signal1(signal1),  
            .signal2(signal2),  
            .signal3(signal3)  
            );  
        -or-  
        macro imacro (signal1, signal2, signal3);  // Acceptable for a short-list macro  
    ```  
      
    **Output:**  
    **Question 1:** What is the format for module instantiation?  
    **Answer:**  
    ```
    The format for module instantiation is:  
        core icore // in case of instantiating a user-defined module  
            (  
            .signal1(signal1),  
            .signal2(signal2),  
            .signal3(signal3)  
            );  
        -or-  
        macro imacro (signal1, signal2, signal3);  // Acceptable for a short-list macro  
    ```

    **Question 2:** What is the role of the `always` block in Verilog?  
    **Answer:** The `always` block in Verilog is used to define sequential logic and execute its contents repeatedly whenever the specified event occurs (e.g., `posedge clk` or `negedge rst_`). It is commonly used for implementing registers, state machines, and other sequential elements.

    **Question 3:** How does the `case` statement function in Verilog?  
    **Answer:** The `case` statement in Verilog is used to implement multi-way branching. It evaluates the given expression and executes the matching case branch. If no match is found, the `default` case executes. This is similar to switch-case structures in other programming languages.

    2. Vary difficulty levels:  
       - Create a mix of basic, intermediate, and advanced questions to suit different audiences.  

    3. Maintain structure and coherence:  
       - Each QA pair should be well-formed, avoiding redundancy or unnecessary complexity.  

    4. Adapt to the content type:  
       - For factual topics, focus on objective and knowledge-based questions.  
       - For conceptual topics, include thought-provoking or explanatory questions.  
       - If the content is research-oriented, provide detailed and in-depth answers.  
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
dataQA = pd.DataFrame(generate_dataset(data, content))
''' NOTE: content được lấy từ Retrieve nội dung !!!'''
