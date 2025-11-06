import pandas as pd
from google.adk.sessions import InMemorySessionService

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
    __session_service = InMemorySessionService()

    def __init__(self, temperature: float, top_p: float, top_k: int, system_prompt: str, golden_data: list[dict] = []):
        self.__temperature = temperature
        self.__top_p = top_p
        self.__top_k = top_k
        self.__system_prompt = system_prompt
        self.__golden_data = golden_data
        self.__accuracy = 0
        self.__session_id = None
        self.__user_id = None

    def __str__(self):
        return f"""
        Temperature: {self.__temperature}
        Top-P: {self.__top_p}
        Top-K: {self.__top_k}
        System Prompt: {self.__system_prompt}
        """

    def get_state(self) -> dict:
        return {
            "temperature": self.__temperature,
            "top_p": self.__top_p,
            "top_k": self.__top_k,
            "system_prompt": self.__system_prompt,
            "golden_data": self.__golden_data
        }
    
    def update_old_state(self):
        self.__was_changed = False
        self.__old_state = self.get_state().copy()
    
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
    def get_accuracy(self):
        return self.__accuracy
    def get_session_id(self):
        return self.__session_id
    def get_session_service(self):
        return self.__session_service
    def get_user_id(self):
        return self.__user_id
    
    def set_temperature(self, new_temp):
        if new_temp != self.__temperature:
            self.__log_change()
            self.__temperature = new_temp
    def set_top_p(self, new_top_p):
        if new_top_p != self.__top_p:
            self.__log_change()
            self.__top_p = new_top_p
    def set_top_k(self, new_top_k):
        if new_top_k != self.__top_k:
            self.__log_change()
            self.__top_k = new_top_k
    def set_system_prompt(self, new_system_prompt):
        if new_system_prompt != self.__system_prompt:
            self.__log_change()
            self.__system_prompt = new_system_prompt
    def set_golden_data(self, new_golden_data: list[dict]):
        if new_golden_data != self.__golden_data:
            self.__log_change()
            self.__golden_data = new_golden_data
    def set_accuracy(self, new_acc):
        self.__accuracy = new_acc
    def set_session_id(self, s_id):
        self.__session_id = s_id
    def set_user_id(self, u_id):
        self.__user_id = u_id

    def get_old_state(self):
        if self.__old_state:
            return self.__old_state
        else:
            return {}

    def output_old_state(self):
        return {
            "temperature": self.__old_state["temperature"],
            "top_p": self.__old_state["top_p"],
            "top_k": self.__old_state["top_k"],
            "system_prompt": self.__old_state["system_prompt"],
        }
    
    def output_state(self):
        return {
            "temperature": self.__temperature,
            "top_p": self.__top_p,
            "top_k": self.__top_k,
            "system_prompt": self.__system_prompt
        }

INIT_TEMPERATURE = 0.1
INIT_TOP_P = 0.3
INIT_TOP_K = 40
INIT_SYSTEM_PROMPT = ''

system_state = State(INIT_TEMPERATURE, INIT_TOP_P, INIT_TOP_K, INIT_SYSTEM_PROMPT, [])