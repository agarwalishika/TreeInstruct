from source.interaction_instructions import *
from source.agent_personas import *
from source.parse_utils import *
import torch
from transformers import pipeline
import re 

class Verifier():
    def __init__(self, problem_statement, correct_code, buggy_code, bug_fixes, bug_description, model, log_file="log.txt"):
        self.problem_statement = problem_statement
        self.correct_code = correct_code
        self.buggy_code = buggy_code
        self.bug_fixes = bug_fixes
        self.bug_description = bug_description
        self.log_file = log_file

        self.init_prompt = verifier_persona + self.problem_statement + self.correct_code
        self.model = model

    def prompt_verifier(self, prompt):
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
            do_sample=False,
            pad_token_id=self.model.tokenizer.eos_token_id
        )
        message = outputs[0]["generated_text"][len(model_prompt):]

        print('prompted verifier')
        log('--- TO VERIFIER: ' + prompt, self.log_file)
        log(f'--- FROM VERIFIER: {message}', self.log_file)

        return message

    def prompt_verifier_state(self, prompt):
        messages = [
            {"role": "system", "content": verifier_persona},
            {"role": "user", "content": prompt + "\nInput:\n\n" + self.problem_statement + self.buggy_code + self.bug_description + \
                        self.bug_fixes + self.correct_code + "\nOutput:\n"}]
        
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
            temperature=0.1,
            top_p=0.9,
            pad_token_id=self.model.tokenizer.eos_token_id
        )

        message = outputs[0]["generated_text"][len(model_prompt):]

        print('prompted verifier state')
        log('--- TO VERIFIER: ' + prompt, self.log_file)
        log(f'--- FROM VERIFIER: {message}', self.log_file)

        return message
    
    def get_state_repr(self):
        prompt = v2v_get_state_repr + yaml_state_repr
        response = self.prompt_verifier_state(prompt)

        return parse_lines_yaml(response)
    
    def assess_misunderstanding(self, instructor_exp, student_exp):
        # check for discrepancy
        x = "is_discrepancy"
        prompt = i2i_discrepancy(instructor_exp, student_exp) + yaml_yes_no(x)
        response = self.prompt_verifier(prompt)

        return parse_yes_no(response, x)
    
    def assess_understanding_of_curr_level(self, instructor_question, current_response):
        x = "did_student_answer_correctly"
        prompt = i2i_correct_answer_breakdown(instructor_question, current_response, self.bug_fixes, self.buggy_code) + yaml_correct_answer
        response = self.prompt_verifier(prompt)
        return parse_correct_answer(response)

    def assess_state_level_understanding(self, instructor_question, current_response, target_representation, is_target, convo_history):
        x = "student_has_sufficient_target_understanding"
        desc = "output \"True\" or \"False\" if the student has sufficient understanding grounded on your 'explanation'"
        q = convo_history[-2]
        a = convo_history[-1]
        c = "\n".join(convo_history[:-2])
        if not is_target: # next state attribute that question is NOT conditionally generated on
            prompt = i2i_address_target_convo_qa(q, a, c, target_representation)
        else:
            prompt = i2i_address_target_qa(q, a, target_representation)
        response = self.prompt_verifier(prompt + yaml_yes_no_desc(x, desc))
        return parse_yes_no(response, x)

    def update_code(self, student_bug_fixes):
        instruction, final_prompt = i2i_apply_bug_fixes(self.buggy_code, student_bug_fixes)

        messages = [
            {"role": "system", "content": instruction},
            {"role": "user", "content": final_prompt + yaml_code_gen}]
        
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
            do_sample=False,
            pad_token_id=self.model.tokenizer.eos_token_id
        )
        message = outputs[0]["generated_text"][len(model_prompt):]

        print('prompted verifier')
        log('--- TO VERIFIER: ' + final_prompt + yaml_code_gen, self.log_file)
        log(f'--- FROM VERIFIER: {message}', self.log_file)

        yaml = message.replace(": \n", ":\n")
        yaml = re.findall(r'(?<=correct_code:\n)((?:.|\n)*?)(?=---)', yaml, re.IGNORECASE)[0]

        log(f'--- PARSED CODE:\n{yaml}', self.log_file)
        return yaml

    def format_bug_fixes(self, fixes, prefix, counter):
        result = ""
        for f in fixes:
            result += f'{prefix}_{counter}: {f}\n'
            counter = chr(ord(counter)+1)
            
        return result

    def check_bug_fixes(self, student_bug_fixes):
        x = "are_fixes_isomorphic"

        correct_bf = re.findall(r'^---\nbug_fixes:\n([\S\s]*)\n---\n$', self.bug_fixes, re.IGNORECASE)[0].split("\n")

        student_bf_formatted = self.format_bug_fixes(student_bug_fixes, 'suggested_bug_fix', '1')
        correct_bf_formatted = self.format_bug_fixes(correct_bf, 'correct_bug_fix', 'a')

        messages = [
            {"role": "system", "content": self.problem_statement},
            {"role": "user", "content": v2v_check_isomorphic_eq_bf(student_bf_formatted, correct_bf_formatted)}]
        
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
            do_sample=False,
            pad_token_id=self.model.tokenizer.eos_token_id
        )

        message = outputs[0]["generated_text"][len(model_prompt):]

        print('prompted verifier state')
        log('--- TO VERIFIER: ' + model_prompt, self.log_file)
        log(f'--- FROM VERIFIER: {message}', self.log_file)

        return parse_bg_iso(message, self.bug_fixes)
    
    def check_code(self, new_code):
        x = "are_snippets_isomorphic"
        messages = [
            {"role": "system", "content": self.problem_statement},
            {"role": "user", "content": v2v_check_semantic_eq(new_code, self.correct_code) + yaml_yes_no(x)}]
        
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
            do_sample=False,
            pad_token_id=self.model.tokenizer.eos_token_id
        )

        message = outputs[0]["generated_text"][len(model_prompt):]

        print('prompted verifier state')
        log('--- TO VERIFIER: ' + model_prompt, self.log_file)
        log(f'--- FROM VERIFIER: {message}', self.log_file)

        return parse_yes_no(message, x)