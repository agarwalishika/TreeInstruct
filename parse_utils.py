import re

def log(text, FILE_NAME):
    with open(f'{FILE_NAME}/log.txt', 'a+') as f:
        f.write('\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n')
        f.write(text)
        f.write('\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n')

def parse_lines_yaml(yaml, tag='state_attribute'):
    try:
        line_exp = re.findall(fr'{tag}_\d*:\s*\n*(.+)', yaml, re.IGNORECASE)
    except:
        yaml = yaml.replace(":\n", ": ")
        line_exp = []
        for line in yaml.split('\n'):
            try:
                line.index('_')
                i = line.index(': ')
                line_exp.append(line[i+2:])
            except:
                continue

    return line_exp

def parse_yes_no(yaml, x):
    # return answer
    explanation = re.findall(r'explanation:\s*\n*(.+)', yaml, re.IGNORECASE)[0]
    answer = re.findall(fr'{x}:\s*\n*(.+)', yaml, re.IGNORECASE)[0] == 'True'

    print(f'EXPLANATION: {explanation}')
    print(f'ANSWER: {answer}')
    return explanation, answer

def parse_correct_answer(yaml):
    # return answer
    relevant = re.findall(r'answer_addresses_question:\s*\n*(.+)', yaml, re.IGNORECASE)[0]
    logical = re.findall(r'answer_has_no_mistakes:\s*\n*(.+)', yaml, re.IGNORECASE)[0]
    explanation = re.findall(r'explanation:\s*\n*(.+)', yaml, re.IGNORECASE)[0]

    print(f'EXPLANATION: {explanation}')
    print(f"ANSWER: {(relevant == 'True') and (logical == 'True')}; (relevant -> {relevant} and logical -> {logical})")
    return explanation, (relevant == 'True') and (logical == 'True')

def parse_bg_iso(message, bug_fixes):
    fix_results = re.findall(r'suggested_bug_fix_\d+_present:\s*\n*(.+)', message, re.IGNORECASE)
    overall = True
    for r in fix_results:
        if "False" in r:
            overall = False
    return overall and (len(fix_results) == (bug_fixes.count('\n') + 1))
