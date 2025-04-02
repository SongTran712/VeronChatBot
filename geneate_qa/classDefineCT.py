from textwrap import dedent
from agno.agent import Agent, RunResponse  # noqa
from pydantic import BaseModel, Field
from agno.models.ollama import Ollama
class TextVerilog(BaseModel):
    Text: str = Field(..., description="This is Text part")
    Code: str = Field(..., description="This is Code part")

class VerilogProcessor:
    def __init__(self, model_id: str, host: str):
        self.model_id = model_id
        self.host = host
        
        self.instruction_rewrite = dedent("""\
            You are a specialized LLM for processing and formatting content that includes both text and code. Your responsibilities include:

                1️⃣ Preserving non-code text exactly as it is, including headings, paragraphs, explanations, and markdown formatting.
                2️⃣ Detecting, extracting, and properly formatting code blocks to improve readability while maintaining correct syntax.
                3️⃣ Ensuring correct indentation and logical structure in all formatted code while keeping inline comments.
                4️⃣ Maintaining blank lines, line breaks, and spacing to preserve logical flow in text and code.

                **IMPORTANT**: Only return the **Expected Output**. Do not include explanations, reasons, or any additional comments.✅ Do NOT modify non-code text. It must remain unchanged.

                                    ✅ Do NOT add explanations, reasons, or additional comments. Only return the Expected Output.

                                    ✅ Detect and format code blocks properly based on language-specific rules.

                                    ✅ Maintain markdown structure: Use <code> tags or triple backticks (```) to wrap code as required.

                ---

                📌 **General Formatting Rules**
                - Preserve introductory and explanatory text without modification.
                - Format code sections while ensuring readability.
                - Maintain correct indentation and logical grouping of statements.
                - Support C, Verilog, and embedded programming languages.

                ---

                **1️⃣ Handling Mixed Text and Code**
                - Leave all non-code text intact. Non-code text is often code explanation, introduction
                - Only apply formatting within code blocks. The code breaks into lines and usually starts with the words 'for' , 'begin' , 'module' , etc.
                - Make sure blank lines are kept exactly the same.

                **Example Input:**
                ```
                -  All comment in all Verilog files has to be in English.
                -  Do not use the include statement in RTL source code. The include statement is replaced by forcing a simulator to search included verilog files.
                -  Do not use the display statement in RTL source code.
                -  Do not assign one Register in two different always blocks.
                -  Do not duplicate a conditional expression more than one place.

                for (reg = 0; reg < count; reg = req + 1)  begin  end
                ```
                **Expected Output:**
                ```
                -  All comment in all Verilog files has to be in English.
                -  Do not use the include statement in RTL source code. The include statement is replaced by forcing a simulator to search included verilog files.
                -  Do not use the display statement in RTL source code.
                -  Do not assign one Register in two different always blocks.
                -  Do not duplicate a conditional expression more than one place.

                for (reg = 0; reg < count; reg = reg + 1) 
                    begin
                    end
                ```

                ---

                **2️⃣ Verilog/SystemVerilog Formatting Rules**
                - Keep `wire`, `reg`, `logic`, `input`, `output` declarations separate.
                - Format `always` blocks with proper indentation.
                - Ensure correct spacing and maintain comments.
                - In case of statements like 'begin', 'end', .. written together with *space*, break the line and put it back in the right position
                **Example_1 Input:**
                ```
                ///////////////////////////////////////&lt;-80 chars // Comments for the following logic
                wire   signal1; assign signal1 = ^signal2; reg [12:0] signal3; always @(posedge clk19 or negedge rst_) begin if (!rst_) begin signal3 <= 13'b0; end else begin if (|signal3) begin signal3[2] <= signal4; end end end
                ```
                **Expected_1 Output:**
                ```verilog
                ///////////////////////////////////////&lt;-80 chars
                // Comments for the following logic
                wire signal1;
                assign signal1 = ^signal2;

                reg [12:0] signal3;

                always @(posedge clk19 or negedge rst_) begin
                    if (!rst_) begin
                        signal3 <= 13'b0;
                    end else begin
                        if (|signal3) begin
                            signal3[2] <= signal4;
                        end
                    end
                end
                ```           
                ---

                **3️⃣ C/C++ Formatting Rules**
                - Each variable and function argument must be declared on a separate line.
                - Maintain proper spacing and indentation for control structures.
                - Ensure `if`, `for`, `while`, and function blocks are well-structured.

                **Example Input:**
                ```
                int a=5,b=10;for(int i=0;i<10;i++){a+=i;b-=i;}return a+b;
                ```
                **Expected Output:**
                ```c
                int a = 5;
                int b = 10;

                for (int i = 0; i < 10; i++) {
                    a += i;
                    b -= i;
                }

                return a + b;
                ```

                ---

                📌 **Summary**
                - **Preserve** all non-code text **exactly as it is**.
                - **Format** only code sections (C, Verilog, Embedded C).
                - **Ensure correct indentation, spacing, and structure**.
                - **DO NOT add explanations, reasons, or additional comments**.
            """)
        
        self.instruction_define = dedent(""""You follow this instruction to excute your mission:
                       1. Code Verilog" – Includes all Verilog syntax, module definitions, port declarations, logic implementations, comments within the code structure, and anything that follows Verilog syntax.

                        2. "Text Explain" – Includes all explanatory descriptions, history logs, comments outside the code structure, and any textual descriptions that provide context about the Verilog code.

            Rules for separation:

                        1. If the content follows Verilog syntax (e.g., module, input, output, parameter, reg, wire, always, assign, case, if), it belongs in "Code Verilog".

                        2. If the content provides background information, history, or instructions without Verilog syntax, it belongs in "Text Explain".

                        3. Comments (//) within Verilog code should remain in "Code Verilog", while large descriptive comment blocks explaining history or context should go into "Text Explain".

            The final output should have two sections: one labeled "Code Verilog" and the other "Text Explain".
            **Input example**
            ''' The name in the title must be the same as the declared name.  Description: One or more paragraph(s) describing in detail the functionality implemented by the function.  Immediately following the function heading should be the function declaration.  The format of these blocks is shown in the following example: ////////////////////////////////////////////////////////////////////////////////<-80 chars // Comments for the following logic wire   signal1; assign signal1 = ^signal2; reg [12:0] signal3; always @( posedge clk19 or negedge rst_ ) begin if (!rst_) begin signal3 <= 13'b0; end else begin if (|signal3) begin signal3[2] <= signal4; end : : end end 
            '''
            **Output example**
            Text = '''The name in the title must be the same as the declared name.  Description One or more paragraph(s) describing in detail the functionality implemented by the function.  Immediately following the function heading should be the function declaration.  The format of these blocks is shown in the following example: '''
            Code = '''////////////////////////////////////////////////////////////////////////////////<-80 chars // Comments for the following logic wire   signal1; assign signal1 = ^signal2; reg [12:0] signal3; always @( posedge clk19 or negedge rst_ ) begin if (!rst_) begin signal3 <= 13'b0; end else begin if (|signal3) begin signal3[2] <= signal4; end : : end end '''
                        """)
            
        self.agent_define = Agent(
            model=Ollama(id=self.model_id, host=self.host),
            description="AI agent for processing mixed Verilog code and explanatory text",
            instructions=self.instruction_define,
            response_model=TextVerilog,
            structured_outputs=True,
            markdown=True,
        )
        
        self.agent_rewrite = Agent(
            model=Ollama(id=self.model_id, host=self.host),
            description="LLM specializing in Verilog code processing and formatting",
            instructions=self.instruction_rewrite,
            markdown=True,
        )
    
    def process_text(self, input_text: str):
        run : RunResponse = self.agent_define.run(input_text)
        return run.content
    
    def format_code(self, input_text: str):
        run: RunResponse = self.agent_rewrite.run(input_text)
        return run.content

# Example usage:
# processor = VerilogProcessor(model_id="gemma3:27b", host="http://192.168.1.20:11434")
# response = processor.process_text("some verilog code")
# print(response.content)
