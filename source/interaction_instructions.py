from source.agent_personas import *

# problem setup
problem_statement = """
<problem>
Write a function `search(x: int, seq: List[int]) -> int` that returns the index of the first occurrence of `x` in `seq`. If `x` is not in `seq`, return the index where `x` should be inserted to keep `seq` sorted. Assume that `seq` is sorted in ascending order.
## Example Cases:
```
search(5, [-1, 5, 8, 10, 12]) => 1
search(-2, [-1, 57, 65]) => 0
search(0, [-120, 60, 78, 100]) => 1
search(77, [-100, -50, 5, 44, 66, 76, 99]) => 6
search(55, [-99, -2, 0]) => 3
```
</problem>
"""

buggy_code = """
<buggy_code>
1. def search(x, seq):
2.  for i in range(len(seq)):
3.    if x < seq[i]:
4.      return i
5.  return len(seq)
</buggy_code>
"""

bug_fixes = """
Do not ask questions that explicitly or implicitly mention the following:
1. Replace `<` with `<=` on line 3
2. On line 3, the function only checks if `x` is less than `seq[i]` and then returns the index `i` where `x` should be inserted. When `x` is in `seq` at position `i`, the function returns the next index `i + 1` instead of the current index `i`.
"""

# YAML formatting prompts

yaml_code_explanation_one_line = """
Format the explanation of the line of code in the following YAML format. Add the answer in one sentence right after the colon without a newline:
---
line_explanation: <code explanation here>
---
"""

yaml_student_answer = """
Answer the above "question" only. 

Format your answer as "student_answer" in the following YAML format. Add your "student_answer" right after the colon without a newline. Do not generate or output any code in your answer, please - keep your answer in English only:
---
student_answer: <student answer to instructor "question">
---
"""

yaml_instructor_answer = """
Answer the above "question" only. 

Format your answer as "instructor_answer" in the following YAML format. Add your "instructor_answer" right after the colon without a newline. Do not generate or output any code in your answer, please - keep your answer in English only:
---
instructor_answer: <instructor answer to "question">
---
"""

yaml_code_explanation = """
$n$ is the number of lines the code has. Format the explanations in the following YAML format, do not deviate from the format, do not add anything except for the line explanation, do not add any newlines to the format, and fill out the following format:
---
line_1_explanation: 
line_2_explanation: 
...
line_n_explanation: 
---
"""

yaml_cqg = """
$k$ is the number of questions you can ask the Student. Format the questions in the following YAML format. Add each question right after the colon without a newline:
---
question_1: <generate question_1 which addresses the "target_understanding">
question_2: <generate question_2 which addresses the "target_understanding">
...
question_k: <generate question_k which addresses the "target_understanding">
---
"""

yaml_yes_no = lambda x: f"""
First provide your thought process (after "explanation"), and then the final answer (after "{x}"), with True or False, right after the colon without a newline. Format your "explanation" and "{x}" in the following YAML format; do not deviate from the format, please:
---
explanation: <output explanation here>
{x}: <output "True" or "False">
---

"""

yaml_yes_no_desc = lambda x, desc: f"""
First provide your thought process (after "explanation"), and then the final answer (after "{x}"), with True or False, right after the colon without a newline. Format your "explanation" and "{x}" in the following YAML format; do not deviate from the format, please:
---
explanation: <output explanation here>
{x}: <{desc}>
---

"""

yaml_correct_answer = f"""
First, provide whether or not the Student addresses the Instructor's question (after tag "answer_addresses_question") and if the answer is logical (has no mistakes/logical errors; answer is after tag "answer_is_correct"), with True or False, right after the colon without a newline. Then, provide your thought process (after tag "explanation"). Format "answer_addresses_question". "answer_has_no_mistakes", and "explanation" in the following YAML format; do not deviate from the format, please:
---
answer_addresses_question: <Does the Student's response (after tag 'Student') address the Instructor's question (after tag 'Instructor')? Output "True or "False">
answer_has_no_mistakes: <Is the Student's response (after tag 'Student') to the Instructor's question (after tag 'Instructor') correct (no logical errors or mistakes)? Output "True or "False">
explanation: <output explanation here for if and how the Student responds to the Instructor correctly or incorrectly>
---
"""

yaml_state_repr = """
$k$ is the number of state attributes that comprise the state representation. Format your state representation in the following YAML format, where explanation contains a brief justification behind how each state attribute has not already been addressed and each state_attribute contains a value describing the necessary concept/bug fix that the student must understand and accomplish respectively. Add each attribute right after the colon without a newline:
---
explanation: <1-3 sentence plan behind which state_attributes to select based on if they directly address the 'bug_description's and 'bug_fixes'>

state_representation:
state_attribute_1: <NECESSARY state_attribute_1 description here>
state_attribute_2: <NECESSARY state_attribute_2 description here>
...
state_attribute_k: <NECESSARY state_attribute_k description here>
---
"""

yaml_code_gen = """
Use the below format when outputting your generated code:
---
correct_code: <new_code here>
---
"""

# conversational helper prompts

s2i_convo_history = """
Your conversation so far with the Student is the following:
"""

i2s_convo_history = """
Your conversation so far with the Instructor is the following:
"""

# Interactions

## Verifier LLM: Get state representations WITHOUT conceptual/syntactical label
v2v_get_state_repr = """
Given the student's buggy code (after tag 'buggy_code'), bug description (after tag 'bug_description'), bug fixes (after tag 'bug_fixes'), and the correct code (after tag 'correct_code') for solving the problem statement (after tag 'problem'), we define the state representation of a set of Instructor-Student interactions as a series of necessary tasks which lead the Student from their 'buggy_code', with bugs described in 'bug_description', to understanding and correcting their conceptual and syntactical mistakes to reach 'correct_code' with the 'bug_fixes'. 

We define a state representation as a list of state attributes, where each attribute denotes a specific task that is NECESSARY for the student to successfully understand and implement the given problem. A NECESSARY task directly addresses at least one of the 'bug_description's and thus, is NOT ALREADY ADDRESSED in 'buggy_code'. In other words, if a task is not successfuly completed, the Student will never be able to correct their 'buggy_code' to 'correct_code'.

If the student's 'buggy_code' shows that they have already understood and implemented a specific task, DO NOT INCLUDE that task as a state attribute since it is REDUNDANT.

The list should be ordered, with earlier attributes/tasks given priority over later ones (e.g., conceptual understanding tasks are a pre-requisite and thus more important than syntactical tasks). The following is an example of how a state representation is explained and constructed (after tags 'example_explanation' and 'example_state_representation') for the given 'example_problem' statement, utilizing the 'example_buggy_code', 'example_bug_description', and 'example_bug_fixes':
---
Input:
example_problem:
Implement a fibonacci sequence using recursion.

example_buggy_code:

    def Fibonacci(n):
        if n <= 0:
            print("Incorrect input")
        elif n == 1:
            return 1
        else:
            return Fibonacci(n-1)

example_bug_description:
On line 7, the function only recursively calls `Fibonacci(n-1)`, which will then only return `1` from the edge case on line 5. Instead, the function should consider that the nth term of the Fibonacci sequence is computed as the sum of the preceding n-1 and n-2 values.

example_bug_fixes:
Replace `return Fibonacci(n-1)` with `return Fibonacci(n-1) + Fibonacci(n-2)` on line 7.

example_correct_code:

    def Fibonacci(n):
        if n <= 0:
            print("Incorrect input")
        elif n == 1:
            return 1
        else:
            return Fibonacci(n-1) + Fibonacci(n-2)
Output:

example_explanation: Based on the 'bug_description', the bug involves an incorrect recursive call, which indicates that the Student does not understand that the Fibonacci sequence requires taking the sum of the preceding two terms for getting the current value. An example where `n` is equal to `2` points this mistake out. Finally, based on the 'bug_fixes', the Student must modify the recursive call to add `Fibonacci(n-2)` in order to reach the `correct_code` state.

example_state_representation:
state_attribute_1: Understand the definition of the Fibonnaci Sequence.
state_attribute_2: Consider the preceding two items in the sequence for computing the current value in the Fibonacci Sequence.
state_attribute_3: Consider the example when `n` is equal to `2`.
state_attribute_4: Correctly recursively call `Fibonacci(n-2)` and add it to the existing `Fibonacci(n-1)`.
---

In the above example format ('example_explanation' and 'example_state_representation'), output an 'explanation' for your plan on which state_attributes to output and the 'state_representation' with all NECESSARY 'state_attribute's for the following 'problem' statement based on 'correct_code', the Student's 'buggy_code', the 'bug_description's, and its respective 'bug_fixes':
"""

## Verifier LLM: Get state representations WITH conceptual/syntactical tag
v2v_get_state_repr_tag = """
Given the student's buggy code and the correct code for solving the problem statement, we define the optimal state of a set of Instructor-Student interactions as a series of tasks which leads the student to understanding their conceptual and syntactical mistakes within the input buggy code. We define a state representation as a list of state attributes, where each attribute denotes a specific task that is NECESSARY for the student to successfully understand and implement the given problem. Each task should also have a tag of whether or not it is a "conceptual" or "syntactical" task.

We define a "conceptual" and a "syntactical" task as the following:

"conceptual" task: A task where the Student addresses a misunderstanding or mistake that they have in the logic or algorithm that underpins their program. These tasks deal with bugs that are related to the way the Student understands (or misunderstands) the problem they are solving and how they apply programming concepts to create a solution. Some examples of conceptual bugs include: (1) incorrectly implementing an algorithm, like sorting or searching, based on flawed logic or (2) ignoring an edge case of a problem.

"syntactical" task: A task where the Student addresses errors in their code that arise from their incorrect use of the programming language’s syntax. Some examples of syntactical bugs include: (1) misspelling a keyword or function name, (2) missing punctuation like semicolons, commas, or parentheses, or (3) an incorrect use of operators, such as using = (assignment) instead of == (equality comparison).

If the student's 'buggy_code' shows that they have already understood and implemented a concept that is used for the correct_code, do NOT INCLUDE the concept/task as a state attribute as it is REDUNDANT.

The list should be ordered, with earlier attributes/tasks given priority over later ones (e.g., conceptual understanding tasks are a pre-requisite and thus more important than syntactical tasks). The following is an example of the state representation for the given example problem statement:
---
example_problem:
Implement a fibonacci sequence using recursion.
---
example_buggy_code:

    def Fibonacci(n):
        if n < 0:
            print("Incorrect input")
        elif n == 0:
            return 0
        elif n == 1:
            return 1
        else:
            return Fibonacci(n-1)
---
example_correct_code:

    def Fibonacci(n):
        if n < 0:
            print("Incorrect input")
        elif n == 0:
            return 0
        elif n == 1 or n == 2:
            return 1
        else:
            return Fibonacci(n-1) + Fibonacci(n-2)
---
example_state_representation:
state_attribute_1: ("Understand the definition of the Fibonnaci Sequence.", "conceptual")
state_attribute_2: ("Consider the preceding two items in the sequence for computing the current value in the Fibonacci Sequence.", "conceptual")
state_attribute_3: ("Consider the edge case when `n` is equal to `2`.", "conceptual")
state_attribute_4: ("Correctly recursively call `Fibonacci(n-2)` and add it to the existing `Fibonacci(n-1)`.", "conceptual")
---

Now do the same for the following problem statement, correct code, and student buggy code:
"""

## Code Explanations

ask_for_student_explanation = lambda x: f"""
Instructor: Can you walk through the logic of your code in line {x}?

Respond as the student, who is learning how to program and believes that their code is correct.
"""


instructor_gt_explanation = lambda x: f""" 
Below is the correct code for the given problem. Can you walk through the logic of your code in line {x}?
"""

## Check for discrepancy (Verifier LLM)
i2i_discrepancy = lambda ins_exp, stud_exp: f"""(1) Is there a discrepancy between the Student explanation (tag "student_explanation") of their code and the Instructor's explanation (tag "instructor_explanation")? A discrepancy exists if the Student explanation does not address the critical points mentioned in the Instructor's explanation.
student_explanation: {stud_exp}
instructor_explanation: {ins_exp}
"""

## Student Tree-Based Understanding

## Conditional Question Generation
i2i_assess_misunderstanding_cqg_code = lambda k: f"""
First, (1) is there a discrepancy between the Student explanation of their code and the Instructor's explanation, and (2) if so, what are {k} follow-up questions with the same level of depth and difficulty that you could ask based on the Student's explanation that would help them understand their bug? 
These questions should help the Student arrive at the answer themselves; do NOT give any direct hints towards the solution (after tag 'bug_fixes').
"""

# Instructor LLM
i2i_cqg_code = lambda k, target_repr: f"""
Based on the buggy code and the target understanding state (under tag "target_understanding"), what are {k} follow-up questions with the same level of depth and difficulty that you could ask based on the Student's explanation that would help them understand their bug? 
These questions should help the Student arrive at the answer themselves; do NOT give any direct hints towards the solution (after tag 'bug_fixes').
---
target_understanding: {target_repr}
"""

i2i_cqg_exp_discrepancy = lambda k, ins_exp, stud_exp, discrepancy: f"""
Based on the discrepancy (tag "discrepancy") between the Student explanation (tag "student_explanation:") and the Instructor explanation (tag "instructor_explanation:"), what are {k} follow-up questions with the same level of depth and difficulty that you could ask based on the Student's explanation that would help them understand their bug? 
These questions should help the Student arrive at the answer themselves; do NOT give any direct hints towards the solution (after tag 'bug_fixes').
---
student_explanation: {stud_exp}
instructor_explanation: {ins_exp}
discrepancy: {discrepancy}
"""

i2i_generate_teaching = lambda q, t, bug_fixes, bug_description: f"""Consider the following target understanding state: {t}. Above you are given 'buggy_code'. Here are some corresponding 'bug_fixes' and 'bug_descriptions' that will fix the 'buggy_code' when applied:

{bug_fixes}

{bug_description}

Can you please provide an appropriate response to this question: {q}""" + yaml_instructor_answer

## Pose Conditional Question to Student
i2s_pose_question = lambda prefix, q: f"""
{prefix} {q}
"""

i2i_generate_initial_q = lambda target_repr, bug_fixes, bug_description: f"""
Based on the buggy code and the target understanding state (under tag "target_understanding"), what is one question (k=1) that you could ask that would help the Student reach the "target_understanding"? 
These questions should help the Student arrive at the answer themselves; do NOT give any direct hints towards the solution (after tag 'bug_fixes').

These questions should help the Student arrive at the answer themselves; do NOT give any direct hints towards the solution (under tag "bug_fixes" and tag "bug_description").

{bug_fixes}

{bug_description}

---
target_understanding: {target_repr}
---
"""

## Pose Conditional Question to Student
i2s_pose_question = lambda prefix, q: f"""
{prefix} {q}
"""

# Given the Student's response to the Instructor's question, do you think the Student's understanding address the below discrepancy?

# Verifier LLM: (PART 1) Check ability to fully comprehend and answer previous level
i2i_prevq = lambda q, r, discrepancy: f"""
Instructor: {q}
Student: {r}

Below is the Student's earlier misunderstanding - based on their above response to the Instructor's above question, do you think their earlier misunderstanding is resolved?

Previous Student Misunderstanding: {discrepancy}

"""

## Instructor LLM: (PART 1) IF NO, go back a level

prefix_prev_level = "That's not exactly correct. Let's go back a step and try another question. "

i2s_prev_level = lambda q: i2s_pose_question(prefix_prev_level, q)

## IF YES, then move onto PART 2:
# Verifier LLM: (PART 2) Check ability to fully comprehend and answer current level.
i2i_correct_response = lambda q, r: f"""
Did the Student correctly respond (after tag 'Student') to the Instructor's question (after tag 'Instructor')?

Instructor: {q}
Student: {r}
"""

i2i_correct_answer_breakdown = lambda q, r, bf, sc: f"""The Student has written code (after tag 'student_code') to solve the problem (after tag 'problem') and is answering a question (after tag 'Student') from the Instructor (after tag 'Instructor') based on their understanding of the 'problem' and their 'student_code'. IF the Student suggests a solution to a bug they identify, also consider the following:

Ensure that the Student's suggestion is isomorphic to any one of the bug fixes mentioned in the provided 'bug_fixes'; if not, then 'answer_has_no_mistakes' should be "False". A Student's suggestion is isomorphic to a bug fix if they (1) have the same conclusion or output, (2) share the same underlying logical structure or pattern, and (3) are convertible to each other through a series of logical transformations.

Answer the following questions and within your reasoning, think about how you would answer the "instructor_question" yourself and include this in your "explanation".:
answer_addresses_question: <Does the Student's response (after tag 'Student') directly answer the Instructor's question (after tag 'Instructor')? Output "True or "False">
answer_has_no_mistakes: <Is the Student's response (after tag 'Student') to the Instructor's question (after tag 'Instructor') logical (no logical errors or mistakes)? Output "True or "False">

---
bug_fixes:
{bf}
---
student_code:
{sc}
---

Instructor: {q}
Student: {r}
"""

i2i_address_target = lambda q, r, t: f"""
Based on the Student's response (after tag 'Student') to the Instructor's question (after tag 'Instructor'), do you believe the Student has generally reached the target level of understanding (after tag 'target_understanding')? Do not be overly critical; if the 'target_understanding' is conceptual, then do not expect an answer discussing code. If the 'target_understanding' is directly relevant to the student's code, then judge accordingly.

Instructor: {q}
Student: {r}

target_understanding: {t}
"""

i2i_address_target_convo_qa = lambda q, r, c, t: f"""
A Student has sufficient understanding of a certain topic (specified at tag "target_understanding") when the responses that they provide to the Instructor (specified in the "conversation_history") would REQUIRE them to comprehend "target_understanding". This can either be demonstrated (1) explicitly, where the Student directly mentions "target_understanding", OR (2) implicitly, where their reasoning is isomorphic to completing the task in "target_understanding". A Student's reasoning is isomorphic to the "target_understanding" if they (1) have the same conclusion or output, (2) share the same underlying logical structure or pattern, and (3) are convertible to each other through a series of logical transformations.

Based on the Student's response (after tag 'student_response') to the Instructor's question (after tag 'instructor_question') and the conversation history (after tag 'conversation_history'), do you believe that the Student needed to sufficiently comprehend the "target_understanding" in order to provide their responses (after tag 'Student' in 'conversation_history') to the Instructor's questions (after tag 'Instructor' in 'conversation_history') throughout the conversation history? Include specific quotes from the "conversation_history" in your "explanation". Within your reasoning, think about how you would answer the "instructor_question" yourself and include this in your "explanation".

---
conversation_history:
{c}
---
_
instructor_question: {q}
student_response: {r}

target_understanding: {t}

"""

i2i_address_target_qa = lambda q, r, t: f"""
A Student has sufficient understanding of a certain topic (specified at tag "target_understanding") when the response that they provide to the Instructor would REQUIRE them to comprehend "target_understanding". This can either be demonstrated (1) explicitly, where the Student directly mentions "target_understanding", OR (2) implicitly, where their reasoning is isomorphic to completing the task in "target_understanding". A Student's reasoning is isomorphic to the "target_understanding" if they (1) have the same conclusion or output, (2) share the same underlying logical structure or pattern, and (3) are convertible to each other through a series of logical transformations.

Do you believe that the Student needed to sufficiently comprehend the "target_understanding" in order to provide their response (after tag 'student_response') to the Instructor's question (after tag 'instructor_question')? Within your reasoning, think about how you would answer the "instructor_question" yourself and include this in your "explanation".

instructor_question: {q}
student_response: {r}

target_understanding: {t}
"""

i2i_address_target_with_code = lambda buggy_code, bug_descriptions, q, r, t: f"""
Based on the below conversation history between the Student and Instructor, the Student's current code (refer to tag 'buggy_code'), and the remaining bugs within their code (refer to tag 'bug_descriptions'), do you believe the Student has reached the below level of understanding (refer to tag 'target_understanding')? The Student should reflect the below level of understanding either through (1) their response (after tag 'Student') to the Instructor's question OR (2) through their code, where the remaining bugs, as described by 'bug_descriptions', DO NOT reflect a LACK of 'target_understanding'). If either (1) or (2) are true, then the Student has reached the 'target_understanding'.

{buggy_code}

{bug_descriptions}

Instructor: {q}
Student: {r}

target_understanding: {t}
"""

v2v_check_semantic_eq = lambda student_code, correct_code: f"""
For the problem description given above (after tag 'problem'), are the below two snippets of code (after tags 'snippet_1' and 'snippet_2') semantically equivalent? In other words, given the same input, do both snippets of code return the same output?

---
snippet_1:
{student_code}
---
snippet_2:
{correct_code}
---
"""

v2v_check_isomorphic_eq_bf = lambda student_bf, correct_bf: f"""
For the problem description given above (after tag 'problem'), you are given two sets of bug fixes (under tags 'suggested_bug_fixes' and 'correct_bug_fixes'). For each bug fix in 'suggested_bug_fixes', is there at least one bug fix in 'correct_bug_fix' that is isomorphic? Two bug fixes are ismorphic if they (1) have the same conclusion or output, (2) share the same underlying logical structure or pattern, and (3) are convertible to each other through a series of logical transformations. Output "True" or "False" as your answer with an explanation.

suggested_bug_fixes: 
{student_bf}

correct_bug_fixes: 
{correct_bf}

Format your answer for each of the k suggested_bug_fixes and provide an explanation for it in the following YAML format:
---
suggested_bug_fix_1_present: <output "True" if 'suggested_bug_fix_1_present' is isomorphic to a bug fix in 'correct_bug_fixes'; output "False" if not>
explanation_bug_fix_1_present: <output a one sentence justification behind your answer for `suggested_bug_fix_1_present`>
suggested_bug_fix_2_present: <output "True" if 'suggested_bug_fix_2_present' is isomorphic to a bug fix in 'correct_bug_fixes'; output "False" if not>
explanation_bug_fix_2_present: <output a one sentence justification behind your answer for `suggested_bug_fix_2_present`>
...
suggested_bug_fix_k_present: <output "True" if 'suggested_bug_fix_k_present' is isomorphic to a bug fix in 'correct_bug_fixes'; output "False" if not>
explanation_bug_fix_k_present: <output a one sentence justification behind your answer for `suggested_bug_fix_k_present`>
---
"""

i2i_apply_bug_fixes = lambda buggy_code, student_bug_fixes: (f"""
Given a set of bug fixes (under tag "student_bug_fixes"), you should apply each bug fix in the set to the buggy code (under tag "buggy_code"). If no bug fixes are provided, then simply return the same code.
Below is an example of buggy code, bug fixes, and your expected example output code (under tag "example_correct_code") where the bug fixes are applied:
---
example_buggy_code:

1.    def Fibonacci(n):
2.        if n < 0:
3.            print("Incorrect input")
4.        elif n == 0:
5.            return 0
6.       elif n == 1:
7.            return 1
8.        else:
9.            return Fibonacci(n-1)
10.

example_bug_fixes:
1. Insert an additional base case after line 7 for `n == 2` and return 1.
2. Replace `return Fibonacci(n-1)` with `return Fibonacci(n-1) + Fibonacci(n-2)` on line 10.

---
example_correct_code:

1.    def Fibonacci(n):
2.        if n < 0:
3.            print("Incorrect input")
4.        elif n == 0:
5.            return 0
6.        elif n == 1:
7.            return 1
8.        elif n == 2:
9.            return 1
10.        else:
11.            return Fibonacci(n-1) + Fibonacci(n-2)
---
""",
f"""
Using this same format, can you apply the following bug fixes (under tag "student_bug_fixes") to the below buggy code (under tag "buggy_code")? Make sure you ONLY apply the bug fixes to their specified line number. Do not make any other additional changes not mentioned in the bug fixes.
Your output code with the bug fixes applied should be under the "correct_code" tag.

{buggy_code}

student_bug_fixes:
{student_bug_fixes}

""")

## Instructor LLM: (PART 2) IF NO, then move on within the current level
prefix_same_level = "That's not entirely correct, let me rephrase the question. "
i2s_curr_level = lambda q: i2s_pose_question(prefix_same_level, q)


## Instructor LLM: (PART 2) IF YES, then move on the next level
prefix_next_level = "That is correct! Let's take a step further. "

# Instructor LLM: (PART 2) Conditioned on the conversation history, generate the next set of questions

i2i_qg = lambda k, prev_qs, convo_history, bug_fixes, bug_description: f"""
Based on the student's current level of understanding, as demonstrated through their conversation history (tag "conversation_history"), what are {k} follow-up questions with the same level of depth and difficulty that you could ask based on the Student's explanation that would help them understand their bug? 
Ensure that the depth and difficulty of your new questions are increased compared to the previous questions asked (tag "previous_question").

previous_questions: 
{prev_qs}

These questions should help the Student arrive at the answer themselves; do NOT give any direct hints towards the solution (under tag "bug_fixes" and tag "bug_description").
{bug_fixes}

{bug_description}

---
conversation_history:
{convo_history}
---
Generate your list of {k} questions:
"""

i2i_generate_child = lambda prev_qs, convo_history, bug_fixes, bug_description, target, explanations: f"""
Based on the student's current level of understanding, as demonstrated through their conversation history (tag "conversation_history"), what is 1 follow-up question with increasing depth and difficulty RELATIVE to the 'previous_questions' that you could ask based on the Student's explanation that would help them reach the "target_understanding"? Make sure that the question addresses the reasons why the Student has not reached the "target_understanding", as detailed in tag "misunderstanding", such that the Student is more likely to resolve these "misunderstanding"s by answering your question.

---
target_understanding: {target}
---

conversation_history:
{convo_history}

previous_questions: 
{prev_qs}

misunderstanding:
{explanations}

These questions should help the Student arrive at the answer themselves; do NOT give any direct hints towards the solution (under tag "bug_fixes" and tag "bug_description").

{bug_fixes}

{bug_description}

Make sure your questions are focused on the below "target_understanding".
---
target_understanding: {target}
---

Generate your question where it leads the Student to reach the "target_understanding". Ensure that the depth and difficulty of your new questions are increased compared to the previous questions asked (tag "previous_questions"):

"""

i2i_generate_sibling = lambda prev_qs, convo_history, bug_fixes, bug_description, target, explanations: f"""
Based on the student's current level of understanding, as demonstrated through their conversation history (tag "conversation_history"), what is 1 follow-up question with the same level of depth and difficulty RELATIVE to the 'previous_questions' that you could ask based on the Student's explanation that would help them reach the "target_understanding"? Make sure that the question addresses the reasons why the Student got the previous question(s) wrong, as detailed in tag "misunderstanding", such that the Student is more likely to resolve these misunderstandings.
You must generate a question such that any correct answer to your question should automatically reflect the "target_understanding" and resolve the "misunderstanding".

---
target_understanding: {target}
---

conversation_history:
{convo_history}

previous_questions: 
{prev_qs}

misunderstanding:
{explanations}

These questions should help the Student arrive at the answer themselves; do NOT give any direct hints towards the solution (under tag "bug_fixes" and tag "bug_description").

{bug_fixes}

{bug_description}

Make sure your questions are focused on the below "target_understanding".
---
target_understanding: {target}
---

Generate your question where it leads the Student to reach the "target_understanding". Ensure that the depth and difficulty of your new question is the same or less than the previous questions asked (tag "previous_questions"):
"""

## Assess Response Misunderstanding (but now based on convo, NOT code explanations)
# this loops the conversation back to i2s_pose_question and i2i_correct_response

# i2i_assess_misunderstanding_cqg_explanation = lambda k: f"""
# First, (1) is there a discrepancy between the Student explanation of their code and the Instructor's explanation, and (2) if so, what are {k} follow-up questions with the same level of depth and difficulty that you could ask based on the Student's explanation that would help them understand their bug? 
# These questions should help the Student arrive at the answer themselves; do NOT give any direct hints towards the solution (after tag 'bug_fix').
# """

# provide more context 
i2s_generate_bug_fixes = lambda convo_history: f"""Are any bug fixes mentioned in the conversation that you have had with the Instructor (under tag "conversation_history")? If no, return "None". If yes, then follow the format below:

First, based on your current understanding of the problem (tag "problem") and your conversation with the Instructor, summarize (after tag "bug_summarization") the bugs in the code explicitly mentioned within the "conversation_history" that you believe will revise your buggy code (after tag "buggy code") to a correct implementation of the "problem" statement. Then, based on this summary, output a list of the explicitly mentioned bug fixes (from "bug_fix_1" to "bug_fix_n", where $n$ is the number of bug fixes to make), each described briefly. 

An example format/wording of a brief bug fix would be: "Replace `i` with `i+1` on line 6."

---
conversation_history:
{convo_history}
---
bug_summarization: <summarize the bugs explicitly mentioned in the "conversation_history" in 1-2 sentences>
bug_fix_1: <bug_fix_1 here>
bug_fix_2: <bug_fix_2 here>
...
bug_fix_n: <bug_fix_n here>
---
"""

i2s_generate_bug_fixes_no_state = lambda convo_history: f"""Based on the conversation that you have had with the Instructor (under tag "conversation_history"), can you suggest a list of bug fixes (described in English) to make that reflects the changes mentioned in the conversation?
An example of a bug fix would be: "Replace `i` with `i+1` on line 6."
---
conversation_history:
{convo_history}
---

$n$ is the number of bug fixes to make. Format the changes in the following YAML format, add it right after the colon without newlines:
---
bug_fix_1: <bug_fix_1 here>
bug_fix_2: <bug_fix_2 here>
...
bug_fix_n: <bug_fix_n here>
---
"""