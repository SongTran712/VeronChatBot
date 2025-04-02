from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.run.response import RunResponse
import pandas as pd
class SummarizeText:
    def __init__(self, model_id: str, host: str):
        self.model_id = model_id
        self.host = host
        
        self.agent = Agent(
            model=Ollama(id=self.model_id, host=self.host),
            description_Sum = """ You are an excellent assistant. Your mission is summarazing the input into shorter paragraph""",
            instruction_Sum = """  """
        )
    def generate_dataset(self, content: str) -> pd.DataFrame:
        Sum_run: RunResponse = self.agent.run(content)
        Sum_text = Sum_run.content
        data_sum = []
        data_sum.append({"summarization":Sum_text})
        return data_sum
# Example usage:
# generator = SummarizeText(model_id="gemma3:27b", host="http://192.168.1.19:11434")
# data_sum = generator.generate_dataset(content)