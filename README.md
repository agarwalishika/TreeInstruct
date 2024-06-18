# Instruct, Not Assist: LLM-based Multi-Turn Planning and Hierarchical Questioning for Socratic Code Debugging

![Framework Diagram of TreeInstruct](https://github.com/agarwalishika/TreeInstruct/blob/main/framework.png)

This repository contains the source code for [**Instruct, Not Assist: LLM-based Multi-Turn Planning and Hierarchical Questioning for Socratic Code Debugging**](https://arxiv.org/abs/2406.11709).

## Links

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Data Format](#data-format)
- [Using GPT-4 as the Instructor/Verifier](#using-gpt-4-as-the-instructor/verifier)
- [Citation](#citation)

## Installation
The code is written in Python 3.8.10. The Python dependencies are summarized in the file `requirements.txt`. You can install them like this:
```
pip install -r requirements.txt
```

## Quick Start
In order to have the Student proxy (`Mistral-7B-Instruct-0.2`) interact with TreeInstruct, you can first download the [**MULTI_DEBUG dataset**](https://drive.google.com/file/d/1qQNX2ImhtCpq9M7I4Ieb2DP3JBFHCBvG/view). Once you unzip the downloaded file (i.e., `tree_instruct_multi_debug_dataset.zip`), you will find three subdirectories, each for one, two, and three conceptual and syntactical bugs being injected within the same programming problems. You should run `extract_leetcode.py` in order to pre-process the dataset into the proper format.

Put the three dataset folders under the main directory `./`, and run the pre-processing code. Then you need to run the following script.
```
./run.sh
```

The following are the primary arguments for TreeInstruct:

- `file` $\rightarrow$ the directory in which the dataset is contained (select one of the bug settings; e.g., `3bug-MULTI-BUG`)
- `bug_num` $\rightarrow$ number of bugs present within the buggy code.
- `log_folder` $\rightarrow$ where the log files of the Verifier-Instrutor and Instructor-Student interactions are stored.

We provide our interactive human evaluation code under the `evaluation` directory.

## Data Format
The following is an example of our dataset format (before running `extract_leetcode.py`):
(1) `<problem>`: problem statement of coding problem

(2) `<bug_fixes>` contains the list of bug fixes that would modify the buggy code into correct code. We maintain the format, `Replace <buggy code> with <correct code> on line <line number>.`

(3) `<bug_desc>` contains the descriptions for each bug present in the code, corresponding to `<bug_fixes>`.

(4) The buggy code is always provided at the very end of each `.py` file.
```
"""
<problem>
Given an array of integers, 
return indices of the two numbers such that they add up to a specific target.

You may assume that each input would have exactly one solution, and 
you may not use the same element twice.

Example:
Given nums = [2, 7, 11, 15], target = 9,
Because nums[0] + nums[1] = 2 + 7 = 9,
return [0, 1].
</problem>
<bug_fixes>
Replace `nums[i] - target` with `target - nums[i]` on line 5.
Replace `d = []` with `d = {}` on line 3.
Add a colon at the end of line 6.
</bug_fixes>
<bug_desc>
On line 5, difference is calculated as nums[i] - target. This results in a negative number, which will not be found. Therefore, the difference needs to be calculated as target - nums[i].
On line 3, d is initialized as a list, but is used as a dictionary later on. This results in a runtime error. d needs to be initialized as a dictionary, by using '{}' to indicate a dictionary instead of a list.
On line 6, a colon is missing from the if-condition, causing it to not terminate. This is a syntactical bug that can be fixed by adding a colon at the end.
</bug_desc>
"""
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
      d = []
      for i in range(len(nums)):
        difference = nums[i] - target
        if difference in d
          return [d[difference], i]
        d[nums[i]] = i
      return d
```

## Using GPT-4 as the Instructor/Verifier
By default, `tree_instruct.py` is the main script for having a `Llama-3-8b` Instructor/Verifier. In the case that you would like to run the code with a GPT-4 Instructor/Verifier, import the following instead of lines 12-13:
```
from agents.verifier_gpt import Verifier
from agents.instructor_gpt import Instructor
```
and replace `llama_8b_model` with `gpt_4` on line 126 instead.

You will just need to set the environment variables, `OPENAI_GPT4_KEY` and `GPT_MODEL_NAME`, based on your own API information:

## Citation
If you find this repository useful, please cite the following paper:
```
@misc{kargupta2024instruct,
    title={Instruct, Not Assist: LLM-based Multi-Turn Planning and Hierarchical Questioning for Socratic Code Debugging},
    author={Priyanka Kargupta and Ishika Agarwal and Dilek Hakkani-Tur and Jiawei Han},
    year={2024},
    eprint={2406.11709},
    archivePrefix={arXiv},
    primaryClass={cs.CL}
}
```