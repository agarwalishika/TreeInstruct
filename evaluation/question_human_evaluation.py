import os
import numpy as np
import pickle as pk
import argparse
import re
from tqdm import tqdm

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    bug_dir = './1BUG-leetcode-master/data_pkls/'
    parser.add_argument('--file', type=str, default='finished_evals/one_bug_gpt4_TI')
    parser.add_argument('--num_bug', type=int, default=3)
    args = parser.parse_args()
    to_eval = args.file
    num_bug = args.num_bug

    if not os.path.exists(f'{to_eval}.csv'):
        with open(f'{to_eval}.csv', "a+") as output_file:
            output_file.write(f"problem,c_success,s_success,num_turns,q1s, q2s, q3s, q1c, q2c, q3c\n")

    with open(f'{to_eval}.csv', "r") as output_file:
        existing = [i.split(",")[0] for i in output_file.read().splitlines()]

    for filename in sorted(os.listdir(bug_dir)):
        
        pkl_f = os.path.join(bug_dir, filename)
        
        problem = filename.split('.')[0] + ".py"
        
        if problem in existing:
            print(f"{problem} already exists! Moving forward...")
            continue

        print("Problem: ", problem)

        with open(f"{to_eval}/{problem}.pkl/convo.txt", "r", encoding='utf8') as convo_f:
            convo = convo_f.read().strip().splitlines()

        num_turns = "\n".join(convo).count("Instructor: ") #len(convo) // 2

        with open(pkl_f, "rb") as problem_pk:
            data = pk.load(problem_pk)
        
        prob_statement = data["problem"]
        fix_desc = data["bug_desc"]
        gt_fixes = data["bug_fixes"]
        example_fix = gt_fixes.split('\n')[2]
        buggy_code = data["buggy_code"]
        correct_code = data["correct_code"]
        convo_history = ""
        
        try:
            with open(f"{to_eval}/{problem}.pkl/bug_fixes.txt", "r") as bf_f:
                fixes = bf_f.read().strip().splitlines()
        except:
            print(problem)
            fixes = ""


        
        print(f"Here is the problem statement:\n\n{prob_statement}\n")
        print(f"Here is the buggy code:\n\n{buggy_code}\n")
        print(f"Here is the bug description:\n\n{fix_desc}\n")
        print(f"Here are the bug fixes:\n\n{gt_fixes}\n")
        print(f"Here are the PREDICTED bug fixes:\n\n{fixes}\n")

        c_success = input(f"CONCEPTUAL success rate: ")
        s_success = input(f"SYNTACTICAL success rate: ")

        syn_scores = []
        con_scores = []
        for i in range(0, len(convo), 6):
            formatted_convo = "\n".join(convo[i:i+2])
            convo_history += "\n".join(convo[i:i+2]) + "\n"
            print(f"TURN {(i//6)+1}/{num_turns}:\n\n{formatted_convo}\n")
            qtype = input("The question asked by the instructor was related to a syntactical bug (0) or conceptual bug (1): ")

            score = []
            prev_qtype = qtype
            qtype = int(qtype)
            score.append(int(input("The question asked by the instructor was relevant to the bugs in the Student code (tag: \"bug_fixes\"). (0: No; 1: Yes): ")))
            score.append(int(input("The question asked by the instructor does NOT explicitly state any of the bug fixes (tag: \"bug_fixes\"). (0: No; 1: Yes): ")))
            score.append(int(input("The question asked by the instructor made the conversation flow in a logical manner and guided the user to solve their problem. (0: No; 1: Yes): ")))
            
            if qtype == 0:
                syn_scores.append(score)
            else:
                con_scores.append(score)

        if len(syn_scores) == 0:
            syn_scores.append([0, 0, 0])
        if len(con_scores) == 0:
            con_scores.append([0, 0, 0])


        final_syn_score = ",".join(str(np.array(syn_scores).mean(axis=0))[1:-1].split())
        final_con_score = ",".join(str(np.array(con_scores).mean(axis=0))[1:-1].split())
        with open(f'{to_eval}.csv', "a+") as output_file:
            output_file.write(f"{problem},{c_success},{s_success},{num_turns},{final_syn_score},{final_con_score}\n")
