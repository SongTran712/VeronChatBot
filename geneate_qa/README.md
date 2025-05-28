# This is a short explanation for this folder "geneate_qa"
![image](https://github.com/user-attachments/assets/a08dc97e-0811-4a93-b88a-c5533fb4ad4e)
## 1. Docling
In the image, we use Docling to extract information from PDFs. We chose Docling because of its ability to segment content—distinguishing between text and images. In this project, we focus on processing text and feeding it into the chatbot. An advanced model can handle technical documents and provide accurate answers, but a smaller model or directly inputting a PDF into a model may result in missing information.
## 2. Process
In this session, we define and reformat the output of Docling. The PDF document (code.pdf) contains not only ordinary text but also technical code in C/C++, Verilog, and other formats. To effectively handle this task, we use a powerful model like Genma3. Additionally, we leverage Groq’s API to process the document efficiently, reducing time consumption and ensuring a seamless workflow. After that we convert them to CSV to handle easier.
## 3. Summarize and QA
1) Summarization We summarize the information extracted from PDFs to build a knowledge base for the chatbot, helping to streamline the search process and reduce processing time. After that, we store it into ElasticSearch to search information.

2) Questions and Answers In this module, we prepare a QA dataset for future use in the RLHF function. Ideally, we would use a structured fine-tuned (SF) model for this task, but due to limitations such as an insufficient number of PDFs and hardware constraints, we have chosen to use the pre-trained model Genma3.
   
