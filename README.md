# Simple program to help sending conversations to students

Run `python sending_conversations_sample.py --help` to see possible commands.

The program will prompt for the Canvas course ID.

It will also prompt for the authentication token if one isn't given in `token.txt` file.

## Quick Start
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python sending_conversations_sample.py --help
```

## Commands
### export
The export command extracts the Canvas user ID and SIS user ID of **active** students in the given course. This command is handy for preparing the values file for sending conversation.

Specify the output file with `--output` parameter. The default is `enrollment_students.csv`

### send-conversation
The send-conversation command sends a unique conversation to each student with a variable embedded in message.

The default template for the conversation is `template.txt`, or specify it with `--template` argument for the command.

The default values for mail-merging into the template is `values.csv`, or specify it with `--values` argument for the command.  The first column of the file needs to be `canvas_user_id`.  Other column names will be used to merge into the template.

See `samples_template.txt` and `sample_values.csv`.

## Examples
```
python sending_conversations_sample.py --help

python sending_conversations_sample.py export --help

python sending_conversations_sample.py export --output new_output.csv

python sending_conversations_sample.py send-conversation --template sample_template.txt --values sample_values.csv
```
