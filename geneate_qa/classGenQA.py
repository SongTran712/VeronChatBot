from agno.agent import Agent
from agno.models.ollama import Ollama
from pydantic import BaseModel, Field
from textwrap import dedent
from agno.run.response import RunResponse
from rich.pretty import pprint
import pandas as pd
class AnswerQuestion(BaseModel):
    question: str = Field(...)
    answer: str = Field(...)
class ThreeAQ(BaseModel):
    aqlist: list[AnswerQuestion]

class QADatasetGenerator:
    def __init__(self, model_id: str, host: str):
        self.model_id = model_id
        self.host = host
        
        self.agent = Agent(
            model=Ollama(id=self.model_id, host=self.host, temperature = 1.25, top_p = 0.7 ),
            description = dedent("""
                You are an expert in generating high-quality, technically detailed question-answer (QA) pairs for building datasets aimed at deepening understanding in major study and research topics, especially those involving hardware design and Verilog/SystemVerilog programming.
            
                Your strength lies in crafting multi-layered questions that test factual recall, conceptual understanding, syntax logic, debugging, best practices, and real-world application.
            
                You generate not just surface-level answers, but detailed, informative, and contextually enriched responses that synthesize input content with your domain expertise. 
                
                Important: Do not use vague or indirect references like “this code”, “that document”, “the snippet above”, etc in the 'Question'.
                
                You MUST generate at least 40 QA pairs.
            """)
            ,
            instructions = dedent("""
                When generating the 40 QA pairs, follow these principles:
            
                1. ✅ Clarity + Relevance + Depth  
                    - Questions must be precise, relevant, and vary in difficulty (basic to advanced). 
                    - You must not use word like "this, that, those .... document, code" make sure use clear thing that you want to ask, fill it in <...>
                    - For code-heavy content (e.g. Verilog), include:
                        - Syntax-based questions (e.g., "What does this code <....> do?")
                        - Functional logic questions (e.g., "What is the purpose of this block of code <...> ?")
                        - Debugging/anti-pattern questions (e.g., "What is wrong with this code <...> ?")
                        - Optimization/best-practice questions (e.g., "How can this <...> be improved?")
                
                2. ✅ Content-based, but Knowledge-Enhanced Answers  
                    - Use the input content as the **primary** source of information.  
                    - However, expand and enrich the answers by using your own knowledge when appropriate.  
                    - Add relevant examples, explanations, or clarifications to improve understanding.  
                    - Avoid repeating the input verbatim. Instead, explain, synthesize, and enhance.
            
                    ***Example 1:***
                    Input:
                    ```verilog
                    assign cond_true = request1 | request2 | request3;
                    always @(posedge clk or negedge rst_) begin
                        if (!rst_) begin end
                        else begin
                            if (cond_true)
                                reg1 <= 2'b10;
                        end
                    end
                    assign wire3 = cond_true ? regtrue : regfalse;
                    ```
                    
                    Output:
                    Question: Why should conditional expressions like `request1 | request2 | request3` be assigned once and reused as a named wire?
                    
                    Answer:
                    Defining `cond_true` as a single wire avoids duplicating the same logic multiple times. This improves **readability**, reduces the risk of **inconsistent edits**, and simplifies **debugging**. In synthesis, having one named signal ensures consistent hardware generation. Reusing named conditions is also a best practice in RTL coding, especially in complex designs where expressions are reused across modules or time domains.
            
                3. ✅ Mixed Question Types  
                    - Combine factual, functional, conceptual, and critical-thinking questions.  
                    - If theory and code are mixed, ask questions that span both theory and practical implementation.
            
                    ***Example 2 (mixed type):***
                    Input: "Do not use `display` in RTL source code."
                    Question: Why is `$display` discouraged in RTL coding and what alternatives should be used in testbenches?
            
                    Answer:
                    `$display` is a simulation-only construct, meaning it doesn't synthesize into hardware and can cause confusion in RTL. Including it violates the clean separation between testbench (non-synthesizable) and RTL (synthesizable) logic. For observability during simulation, `$display` should be used only in testbenches. For debugging RTL, waveform inspection via signal monitoring tools (e.g., VCD files, signal viewers) is the preferred method.
            
                4. ✅ Keep Coherence + Structure
                    - Each QA pair should be self-contained.
                    - Avoid redundancy across questions.
                    - Structure answers in paragraphs or bullet points if helpful.
                
                5. ✅ If input is mixed (theory + code), ask across both:
                    - Don't just ask about the code syntax.
                    - Include questions about the reasoning behind rules, design methodology, and practical consequences.
            """),
            response_model=ThreeAQ,
            structured_outputs=True,
        )
    
    def generate_dataset(self, content: str) -> pd.DataFrame:
        structured_output_response: RunResponse = self.agent.run(content)
        QAstack = structured_output_response.content
        
        dataQA = []
        for item in QAstack.aqlist:
            dataQA.append({"question": item.question, "answer": item.answer})
        return dataQA

# Example usage:
# generator = QADatasetGenerator(model_id="gemma3:27b", host="http://192.168.1.19:11434")
# dataQA = generator.generate_dataset(content)
