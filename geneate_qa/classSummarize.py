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
            description= """ You are an excellent assistant. Your mission is summarazing the input into shorter paragraph""",
            instructions= """ Provide a wise and insightful summary of the following input, preserving its core message while naturally integrating key keywords. 
            The summary should be thought-provoking and reflective, offering deeper understanding or perspective."""
        )
    def generate_dataset(self, content: str) -> pd.DataFrame:
        Sum_run: RunResponse = self.agent.run(content)
        Sum_text = Sum_run.content
        return Sum_text
    