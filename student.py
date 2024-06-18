from interaction_instructions import *
from agent_personas import *
from parse_utils import *
from transformers import pipeline
import re 

class Student():
    def __init__(self, problem_statement, buggy_code, model, log_file="log.txt"):
        self.problem_statement = problem_statement
        self.buggy_code = buggy_code
        self.log_file = log_file

        self.model = model
        self.init_prompt = student_persona + self.problem_statement + self.buggy_code
    
    def prompt_student(self, prompt, suffix="", do_sample=True):
        final_prompt = "<s>[INST]" + self.init_prompt + prompt + "[/INST]" + suffix
        if do_sample:
            response = self.model(final_prompt, 
                                do_sample=do_sample,
                                top_k=10,
                                num_return_sequences=1, 
                                max_new_tokens=200,
                                pad_token_id=self.model.tokenizer.eos_token_id)[0]
        else:
            response = self.model(final_prompt, 
                                do_sample=do_sample,
                                num_return_sequences=1, 
                                max_new_tokens=200,
                                pad_token_id=self.model.tokenizer.eos_token_id)[0]
            
        print('prompted student')
        log('--- TO STUDENT: ' + prompt, self.log_file)
        log('--- FROM STUDENT: ' + response['generated_text'].split('[/INST]')[-1], self.log_file)
        return response['generated_text']
        # response = ''
        # return response
    
    def parse_student_exp(self, yaml):
        yaml = yaml.replace(":\n", ": ").replace(": \n", ": ")
        yaml = yaml.split('[/INST]')[-1]
        yaml = re.findall(r'line_explanation: (.+)\n', yaml, re.IGNORECASE)[0] #yaml.split('[/INST] line_explanation: ')[1]
        if "\n" in yaml:
            yaml = yaml.split("\n")[0]
        print(yaml)
        return yaml
    
    def parse_student_answer(self, yaml):
        yaml = yaml.replace(":\n", ": ").replace(": \n", ": ")
        yaml = yaml.split('[/INST]')[-1]
        yaml = re.findall(r'student_answer:\s*\n*([\S\s]*)', yaml, re.IGNORECASE)[0]
        if "\n" in yaml:
            yaml = yaml.split("\n")[0]
        print(yaml)
        return yaml

    def generate_bug_fixes(self, convo_history):
        prompt = i2s_generate_bug_fixes('\n'.join(convo_history))
        yaml = self.prompt_student(prompt, do_sample=False)
        yaml = yaml.split('[/INST]')[-1]
        yaml = re.findall(r'bug_fix_.:\s*(.*)', yaml, re.IGNORECASE)
        return yaml

    def ask_student(self, question):
        # response = self.prompt_student(question + yaml_student_answer, "\nstudent_answer: ")
        response = self.prompt_student(f"question: {question}\n" + yaml_student_answer, suffix="\nstudent_answer: ")
        return self.parse_student_answer(response)