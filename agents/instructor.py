from source.interaction_instructions import *
from source.agent_personas import *
from source.parse_utils import *
import torch
from transformers import pipeline
import re


class Instructor():
    def __init__(self, problem_statement, buggy_code, bug_fixes, bug_description, model, log_file="log.txt"):
        self.problem_statement = problem_statement
        self.buggy_code = buggy_code
        self.bug_fixes = bug_fixes
        self.bug_description = bug_description
        self.log_file = log_file

        self.init_prompt = instructor_persona + self.problem_statement + self.buggy_code
        self.model = model


    def prompt_instructor(self, prompt):
        messages = [
            {"role": "system", "content": self.init_prompt},
            {"role": "user", "content": prompt}]
        
        model_prompt = self.model.tokenizer.apply_chat_template(messages, 
                                                        tokenize=False, 
                                                        add_generation_prompt=True)

        terminators = [
            self.model.tokenizer.eos_token_id,
            self.model.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

        outputs = self.model(
            model_prompt,
            max_new_tokens=1024,
            eos_token_id=terminators,
            do_sample=True,
            temperature=0.3,
            top_p=0.9,
            pad_token_id=self.model.tokenizer.eos_token_id
        )
        message = outputs[0]["generated_text"][len(model_prompt):]

        print('prompted instructor')
        log('--- TO INSTRUCTOR: ' + prompt, self.log_file)
        log(f'--- FROM INSTRUCTOR: {message}', self.log_file)
        return message
        
    
    def generate_candidate_questions(self, convo_history=None, prev_qs=None, target=None, explanation="", tag="initial"):
        # conditional question genration
        ch = "\n".join(convo_history)
        if tag == "initial":
            prompt = i2i_generate_initial_q(target, self.bug_fixes, self.bug_description) + yaml_cqg
        elif tag == "same":
            prompt = i2i_generate_sibling(prev_qs, ch, self.bug_fixes, self.bug_description, target, explanation) + yaml_cqg
        else: # next level of questions
            prompt = i2i_generate_child(prev_qs, ch, self.bug_fixes, self.bug_description, target, explanation) + yaml_cqg

        candidate_questions = self.prompt_instructor(prompt)
        candidate_questions = parse_lines_yaml(candidate_questions, tag='question')

        return candidate_questions
    
    def generate_teaching(self, question, target_rep):
        prompt = i2i_generate_teaching(question, target_rep, self.bug_fixes, self.bug_description)
        yaml = self.prompt_instructor(prompt)
        yaml = yaml.replace(":\n", ": ").replace(": \n", ": ")
        yaml = re.findall(r'instructor_answer:\s*\n*([\S\s]*)', yaml, re.IGNORECASE)[0]
        if "\n" in yaml:
            yaml = yaml.split("\n")[0]
        print(yaml)
        return yaml