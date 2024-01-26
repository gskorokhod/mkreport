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
        report_dir_name = ''
        report_file_name = ''
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)

            subprocess.run(['git', 'clone', REPORT_TEMPLATE_REPO, temp_dir_path])

            if typesetting == 'quarto':
                report_dir_name = 'quarto-report'
                report_file_name = 'report.qmd'
            elif typesetting == 'markdown':
                report_dir_name = 'report'
                report_file_name = 'report.md'
            else:
                print(f'Unknown typesetting system {typesetting}!')

            path = temp_dir_path / report_dir_name
            shutil.copytree(path, fpath, dirs_exist_ok=True)

        update_report_metadata(fpath / report_file_name, ans)

        if should_use_git:
            subprocess.run(['git', 'init'], cwd=fpath)
            subprocess.run(['git', 'add', './*'], cwd=fpath)
            subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=fpath)

        print(f"Report template set up at {fpath}")
