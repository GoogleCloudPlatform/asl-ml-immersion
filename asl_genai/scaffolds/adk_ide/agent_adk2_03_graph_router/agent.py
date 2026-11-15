# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from google.adk import Agent
from google.adk import Workflow
from google.adk import Event
from pydantic import BaseModel

MODEL = "gemini-2.5-flash"

process_message = Agent(
   name="process_message",
   model=MODEL,
   instruction="""Classify user message into either "BUG", "CUSTOMER_SUPPORT",
     or "LOGISTICS". If you think a message applies to more than one category,
     reply with a comma separated list of categories.
  """,
   output_schema=str,
)

def router(node_input: str):
   routes = node_input.split(",")
   routes = [route.strip() for route in routes]
   return Event(route=routes)

def response_1_bug():
   return Event(message="Handling bug...")

def response_2_support():
   return Event(message="Handling customer support...")

def response_3_logistics():
   return Event(message="Handling logistics...")

root_agent = Workflow(
  name="routing_workflow",
  edges=[
      ("START", process_message, router),
      ( router,
          {
              "BUG": response_1_bug,
              "CUSTOMER_SUPPORT": response_2_support,
              "LOGISTICS": response_3_logistics,
          }
      )
  ],
)
