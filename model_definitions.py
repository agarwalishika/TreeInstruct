from interaction_instructions import *
from agent_personas import *
from parse_utils import *
import torch
from transformers import pipeline
import os
from openai import AzureOpenAI

llama_8b_model = pipeline("text-generation", 
                    model="meta-llama/Meta-Llama-3-8B-Instruct",
                    model_kwargs={"torch_dtype": torch.bfloat16},
                    trust_remote_code=True, 
                    device_map='auto')

mistral_model = pipeline("text-generation", 
                    model="mistralai/Mistral-7B-Instruct-v0.2", 
                    trust_remote_code=True, 
                    device_map='auto')

gpt_35 = AzureOpenAI(
            api_key = os.environ['OPENAI_GPT3_KEY'],  
            api_version = "2024-02-01",
            azure_endpoint = os.environ['AZURE_ENDPOINT_GPT3']
        )

gpt_4 = AzureOpenAI(
            api_key = os.environ['OPENAI_GPT4_KEY'],
            api_version = "2024-02-01",
            azure_endpoint = os.environ['AZURE_ENDPOINT_GPT4']
)