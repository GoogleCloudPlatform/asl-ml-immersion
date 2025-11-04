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

    __old_state: dict
    __was_changed = False

    def __init__(self, temperature: float, top_p: float, top_k: int, system_prompt: str, golden_data: list[dict] = None):
        self.__temperature = temperature
        self.__top_p = top_p
        self.__top_k = top_k
        self.__system_prompt = system_prompt
        self.__golden_data = golden_data

    def __str__(self):
        return str(self.get_state())

    def get_state(self) -> dict:
        return {
            "temperature": self.__temperature,
            "top_p": self.__top_p,
            "top_k": self.__top_k,
            "system_prompt": self.__system_prompt,
            "golden_data": self.__golden_data
        }
    
    def __log_change(self):
        if not self.__was_changed:
            self.__old_state = {
                "temperature": self.__temperature,
                "top_p": self.__top_p,
                "top_k": self.__top_k,
                "system_prompt": self.__system_prompt,
                "golden_data": self.__golden_data
            }
            self.__was_changed = True

    def get_temperature(self):
        return self.__temperature
    def get_top_p(self):
        return self.__top_p
    def get_top_k(self):
        return self.__top_k
    def get_system_prompt(self):
        return self.__system_prompt
    def get_golden_data(self):
        return self.__golden_data
    
    def set_temperature(self, new_temp):
        if new_temp != self.__temperature:
            self.__log_change()
            self.__temperature = new_temp
    def set_topP(self, new_top_p):
        if new_top_p != self.__top_p:
            self.__log_change()
            self.__top_p = new_top_p
    def set_topK(self, new_top_k):
        if new_top_k != self.__top_k:
            self.__log_change()
            self.__top_k = new_top_k
    def set_system_prompt(self, new_system_prompt):
        if new_system_prompt != self.__system_prompt:
            self.__log_change()
            self.__system_prompt = new_system_prompt

    def get_old_state(self):
        if self.__old_state:
            return self.__old_state
        else:
            return {}
