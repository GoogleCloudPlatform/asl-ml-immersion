import pandas as pd


class State:
    ## Hyperparameters
        # Temperature (float)
        # Top_p (float)
        # Top_k (int)
    ## System Prompt (str)
    ## Golden Q&As (pd dataframe)
    ## TODO: Docs
    ##
    def __init__(self, temperature: float, top_p: float, top_k: int, system_prompt: str, golden_data: list[dict] = None):
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.system_prompt = system_prompt
        self.golden_data = golden_data

    def get_state(self) -> dict:
        # Not sure that the whole dataset should be printed to the screen
        return {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "system_prompt": self.system_prompt,
            #"golden_data": self.golden_data
        }