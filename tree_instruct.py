from interaction_instructions import *
from agent_personas import *
from parse_utils import *
import torch
import pickle
import os
from transformers import pipeline
import re
import argparse
import glob
from model_definitions import *
from verifier import Verifier
from instructor import Instructor
from student import Student

def fix_misunderstanding(student: Student, instructor: Instructor, verifier: Verifier, state_representation, target_rep):
    global num_questions
    global convo_history
    global buggy_code
    level = 0 # level 0 is asking about misunderstandings with code
    level_questions = {}
    level_indices = {}
    is_student_done = False
    level_explanations = {}

    # error handling
    level_questions[-1] = [f'Can you walk through the logic of your code?']

    prefix = ""

    # discrepancy, _ = verifier.assess_misunderstanding(instructor_exp, student_exp)
    candidate_questions = instructor.generate_candidate_questions(convo_history=convo_history, target=target_rep, tag="initial")

    while not is_student_done:
        # assess core misunderstanding -> get the k questions to ask student     
        if level not in level_questions.keys():
            level_questions[level] = candidate_questions
            level_indices[level] = 0 # setting i

        # get student answer for question i at level l
        # TODO: DEBUG THIS
        instructor_question = prefix + level_questions[level][level_indices[level]]
        convo_history.append("Instructor: " + instructor_question)
        student_question_response = student.ask_student(instructor_question)
        convo_history.append("Student: " + student_question_response)
        level_indices[level] += 1
        
        # use verifier to see if student understands the curr level questions
        clu_explanation, is_curr_level_understand = verifier.assess_understanding_of_curr_level(instructor_question, student_question_response)
        if is_curr_level_understand:
            # TODO: ADD CONDITION THAT TAKES IN TARGET ATTRIBUTE AND SEE IF IT IS RESOLVED --> STOP
            # [[attribute_1, 2, ...], [False, False,..]]
            target_idx = state_representation[0].index(target_rep)
            for i in range(target_idx, len(state_representation[0])):
                rep_task = state_representation[0][i]

                # is this state repr already true?
                if state_representation[1][i]:
                    continue

                # is this state attribute actually resolved?
                exp, flag = verifier.assess_state_level_understanding(instructor_question, student_question_response, rep_task, i == target_idx, convo_history)
                # if it is resolved -> update state representation and move onto next attribute (update is_student_done bc we need to generate bug fixes anyway)
                # if it is not resolved -> if no progression (i == idx), just prefix_next_level;
                #                       -> if progression (i > idx), ask student to generate bug fixes + ask instructor/verifier to update the code -> return state_repr + new code
                if flag:
                    state_representation[1][i] = True
                    is_student_done = True
                elif i == target_idx:
                    level_explanations[level] = exp
            
            if not is_student_done:
                level += 1
                prefix = prefix_next_level

        else:
            # no change in level
            prefix = prefix_same_level
            level_explanations[level] = clu_explanation

        with open(f'{LOG_FOLDER}/{FILE_NAME}/convo.txt', 'a+') as f:
            try:
                f.write(f'Instructor: {instructor_question}\n')
                f.write(f'Student: {student_question_response}\n')
                # f.write(f'Verifier: \n\t Previous Level: {is_prev_level_understand}, {plu_explanation}\n')
                f.write(f'\tCurrent Target: {target_rep}\n')
                f.write(f'\tCurrent Level: {is_curr_level_understand}, {clu_explanation}\n')
                f.write(f'\tCurrent State Representation: {state_representation[1]}\n\n')
            except:
                f.write(f'\tCurrent Level: N/A, N/A\n')
        
        # generate new questions
        if not is_student_done:
            # check to add teaching
            if not is_curr_level_understand and (len(level_questions[level]) >= 3 or level >= 7):
                teaching = instructor.generate_teaching(level_questions[level][0], target_rep)
                candidate_questions = f"Consider the following: {teaching}\n{level_questions[level][-1]}"
                level_questions[level].append(candidate_questions)

                log(f'------------------------------------------------------------------------\nADDING TEACHING:{candidate_questions}\n------------------------------------------------------------------------', os.path.join(LOG_FOLDER, FILE_NAME))
            elif not is_curr_level_understand: # same level
                candidate_questions = instructor.generate_candidate_questions(convo_history=convo_history, prev_qs='\n'.join(level_questions[level]), target=target_rep, explanation=level_explanations[level], tag="same")
                level_questions[level].extend(candidate_questions)
            else: # next level
                candidate_questions = instructor.generate_candidate_questions(convo_history=convo_history, prev_qs='\n'.join(level_questions[level - 1]), target=target_rep, explanation=level_explanations[level-1], tag="next")
                

    # generate new code
    student_bug_fixes = student.generate_bug_fixes(convo_history)
    with open(f'{LOG_FOLDER}/{FILE_NAME}/bug_fixes.txt', 'a+') as f:
        f.write(f'{student_bug_fixes}\n')
    if len(student_bug_fixes):
        # new_code = verifier.update_code(student_bug_fixes)
        is_code_correct = verifier.check_bug_fixes(student_bug_fixes)
        # _, is_code_correct = verifier.check_code(new_code)

        if is_code_correct:
            state_representation[1] = [True]*len(state_representation[1])
    else:
        new_code = buggy_code
    return state_representation, buggy_code

def run():
    global problem_statement, correct_code, buggy_code, bug_fixes, bug_description, LOG_FOLDER, FILE_NAME
    log_file = os.path.join(LOG_FOLDER, FILE_NAME)
    verifier = Verifier(problem_statement, correct_code, buggy_code, bug_fixes, bug_description, model=llama_8b_model, log_file=log_file)
    instructor = Instructor(problem_statement, buggy_code, bug_fixes, bug_description, model=verifier.model, log_file=log_file)
    student = Student(problem_statement, buggy_code, model=mistral_model, log_file=log_file)

    did_student_understand = False

    # get state representation based on student initial progress
    # starting point: buggy code
    # how to we get to ending point: correct code
    
    # TODO: CHECK STATE REPRESENTATION FOR MULTIPLE BUGS AND IF WE NEED TO BUILD IT OUT BLOCK BY BLOCK
    state_attributes = verifier.get_state_repr()
    state_repr = [state_attributes, [False]*len(state_attributes)]
    temp = ""
    for x, y in zip(state_repr[0], state_repr[1]):
        temp += f"{x}, {y}\n"
    
    log(f"State Representation: {temp}", os.path.join(LOG_FOLDER, FILE_NAME))

    global num_questions
    global convo_history
    
    while not did_student_understand:
        if False in state_repr[1]:
            target = state_repr[0][state_repr[1].index(False)]
            state_repr, student_new_code = fix_misunderstanding(student, instructor, verifier, state_repr, target)
            buggy_code = student_new_code
            convo_history = []

            temp = ""
            for x, y in zip(state_repr[0], state_repr[1]):
                temp += f"{x}, {y}\n"
            log(f"State Representation: {temp}", os.path.join(LOG_FOLDER, FILE_NAME))
        else:
            did_student_understand = True
            with open(f'{LOG_FOLDER}/{FILE_NAME}/correct_code.txt', 'w+') as f:
                f.write(buggy_code)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str, default='..data_pkls/')
    parser.add_argument('--bug_num', type=int, default=1)
    parser.add_argument('--log_folder', type=str, default='single_bug_llama')

    args = parser.parse_args()
    LOG_FOLDER = args.log_folder

    try:
        os.mkdir(f'{LOG_FOLDER}')
    except:
        hi = 9

    files = glob.glob(f'{args.file}/*.pkl')
    for f in files:
        try:
            FILE_NAME = f[f.rfind('/')+1:] #re.findall(r'data_pkls/(.+).pkl', args.file, re.IGNORECASE)[0]
            print("HELLO", FILE_NAME)
            try:
                os.mkdir(f'{LOG_FOLDER}/{FILE_NAME}')
            except OSError:
                if os.path.exists(os.path.join(f'{LOG_FOLDER}/{FILE_NAME}', 'log.txt')):
                    os.remove(os.path.join(f'{LOG_FOLDER}/{FILE_NAME}', 'log.txt'))

                if os.path.exists(os.path.join(f'{LOG_FOLDER}/{FILE_NAME}', 'bug_fixes.txt')):
                    os.remove(os.path.join(f'{LOG_FOLDER}/{FILE_NAME}', 'bug_fixes.txt'))

                if os.path.exists(os.path.join(f'{LOG_FOLDER}/{FILE_NAME}', 'convo.txt')):
                    os.remove(os.path.join(f'{LOG_FOLDER}/{FILE_NAME}', 'convo.txt'))

                if os.path.exists(os.path.join(f'{LOG_FOLDER}/{FILE_NAME}', 'correct_code.txt')):
                    os.remove(os.path.join(f'{LOG_FOLDER}/{FILE_NAME}', 'correct_code.txt'))

            extracted_data = pickle.load(open(f, 'rb'))
            problem_statement = extracted_data['problem']
            buggy_code = extracted_data['buggy_code']

            bug_fixes = extracted_data['bug_fixes']
            if args.bug_num == 1:
                first_bug_fix = re.findall(r'^---\nbug_fixes:\n([\S\s]*)\n---\n$', bug_fixes, re.IGNORECASE)[0].split("\n")[0]
                bug_fixes = re.sub(r'^---\nbug_fixes:\n[\S\s]*\n---\n$', f'---\nbug_fixes:\n{first_bug_fix}\n---\n', bug_fixes)
            # else:
            #     bug_fixes = re.findall(r'^---\nbug_fixes:\n([\S\s]*)\n---\n$', bug_fixes, re.IGNORECASE)[0]


            bug_description = extracted_data['bug_desc'] # not a typo
            correct_code = extracted_data['correct_code']
            unit_tests = ''#extracted_data['unit_tests']

            num_questions = 3 # k
            convo_history = []

            log(f"problem statement:\n{problem_statement}\nbuggy_code:\n{buggy_code}\ncorrect_code:\n{correct_code}\nbug_fixes:\n{bug_fixes}", os.path.join(LOG_FOLDER, FILE_NAME))

            run()
        except:
            with open('FAILURE_CASES.txt', 'a+') as f:
                f.write(f'{FILE_NAME}\n')

