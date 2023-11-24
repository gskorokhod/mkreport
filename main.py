import os
import shutil
import subprocess
import tempfile

from dotenv import load_dotenv

from ask.question_set import QuestionSet
from ask.questions import *
from utils import dict_pop, to_snake_case, update_report_metadata

load_dotenv()

STUDENT_ID = os.getenv('STUDENT_ID', None)
REPORT_TEMPLATE_REPO = os.getenv('REPORT_TEMPLATE_REPO')
REPORTS_DIR = os.getenv('REPORTS_DIR', '~/Documents/Reports/')

question_set = QuestionSet([
    TextQuestion("title", "Enter the report title", required=True),
    TextQuestion("author", "Enter your student id", required=True, default=STUDENT_ID),
    DateTimeQuestion("date",
                     "Enter the report date",
                     required=True,
                     default=datetime.now(),
                     datetime_formats=['%d %m %Y', '%d-%m-%Y', '%d %B %Y', '%d %b %Y'],
                     n_prompts_to_show=1),
    TextQuestion("tutor", "Enter your tutor's name", required=False, default=None),
    ChoiceQuestion('typesetting',
                   'Which typesetting system do you want to use?',
                   required=True,
                   default='markdown',
                   options=['quarto', 'markdown']),
    PathQuestion('path',
                 'Where would you like to store the report files?',
                 required=True,
                 default=Path(REPORTS_DIR)),
    BoolQuestion('git',
                 'Do you want to use Git for version control?',
                 required=True,
                 default=False),
])

if __name__ == '__main__':
    ans = question_set.ask()

    typesetting = dict_pop(ans, 'typesetting')

    fpath = Path(dict_pop(ans, 'path')) / to_snake_case(ans['title'])
    fpath = fpath.expanduser().resolve()
    should_use_git = dict_pop(ans, 'git')

    if fpath.exists():
        print(f"The directory {fpath} already exists. Exiting.")
    else:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)

            subprocess.run(['git', 'clone', REPORT_TEMPLATE_REPO, temp_dir_path])

            if typesetting == 'quarto':
                path = temp_dir_path / 'quarto-report'
                shutil.copytree(path, fpath, dirs_exist_ok=True)
            elif typesetting == 'markdown':
                path = temp_dir_path / 'report'
                shutil.copytree(path, fpath, dirs_exist_ok=True)
            else:
                print(f'Unknown typesetting system {typesetting}!')

        update_report_metadata(fpath / 'report.md', ans)

        if should_use_git:
            subprocess.run(['git', 'init'], cwd=fpath)

        print(f"Report template set up at {fpath}")
