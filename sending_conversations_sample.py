# -*- coding: utf-8 -*-
"""
@author: Jeremy H. & Victor S.
"""

import requests, pandas as pd, click
from string import Template

## Configure these default values
# template file for the conversation
default_template_file = "template.txt"
# values file to merge into the template.
# the first column needs to be the canvas_user_id
default_conversation_values = "values.csv"
# enrollments output csv
default_enrollments_export_file = "enrollment_students.csv"

# Canvas api URL
# base_url = "https://canvas.ubc.ca/api/v1"
# base_url = "https://ubc.test.instructure.com/api/v1"
base_url = "http://localhost:8900/api/v1"
# where the Canvas API authentication token is store. if not provided, user will be prompted for the token
token_file = "token.txt"


def _merge_message(template_str, **values):
    t = Template(template_str)
    return t.substitute(**values)

def get_course_info(token, course_id):
    url = base_url + '/courses/{}'.format(course_id)
    resp = requests.get(url,
        headers= {'Authorization': 'Bearer ' + token})

    if resp.ok:
        return resp.json()
    else:
        raise Exception('Problem getting course info')


def export_course_active_enrollments(token, course_id, output_filename, type='StudentEnrollment'):
    url = base_url + '/courses/{}/enrollments?state=active&type[]={}'.format(course_id, type)
    resp = requests.get(url,
        headers= {'Authorization': 'Bearer ' + token})

    if resp.ok:
        data = resp.json()
        df = pd.DataFrame(columns=['canvas_user_id','sis_user_id'])
        index = 0
        for enrollment in data:
            df.loc[index] = [str(enrollment['user_id']), str(enrollment['sis_account_id'])]
            index += 1

        df.to_csv(output_filename, sep='\t', encoding='utf-8', index=False)
    else:
        raise Exception('Problem getting enrollments')


def post_conversations(token, course_id, canvas_user_id, subject, message):
    url = base_url + '/conversations'
    payload = {
        'recipients[]': [canvas_user_id],
        'subject': subject,
        'context_code': 'course_{}'.format(course_id),
        'body': message,
        }
    resp = requests.post(url,
        params = payload,
        headers= {'Authorization': 'Bearer ' + token})

    if not resp.ok:
        print(resp.text)
        raise Exception('Problem posting conversations')

def merge_and_send_conversation(token, course_id, template_file, conversation_values_file):
    template_str = None
    with open(template_file, 'r') as f:
        template_str = f.read()

    df = pd.read_csv(conversation_values_file, sep='\t', index_col=False)
    print("Here are the first few conversations as examples:")
    for _, row in df.head().iterrows():
        print('---- {} ----'.format(row['canvas_user_id']))
        print(_merge_message(template_str, **row.to_dict()))
        print('--------')

    if not click.confirm('Do you want to proceed', default=False, prompt_suffix='? '):
        return

    for _, row in df.iterrows():
        print('Sending to {}'.format(row['canvas_user_id']))
        post_conversations(token, course_id, row['canvas_user_id'], 
            'subject of the conversations', 
            _merge_message(template_str, **row.to_dict()))


@click.group()
@click.pass_context
def do_action(ctx):
    token = None
    try:
        with open(token_file, 'r') as f:
            token = f.readline()
            print("Got token from token.txt")
    except IOError:
        token = click.prompt("Enter your Canvas Token", hide_input=True)

    course_id = input("Enter your Canvas course ID: ")
    course_info = get_course_info(token, course_id)
    print('We are going to work on the course "{}"'.format(course_info['name']))

    ctx.ensure_object(dict)
    ctx.obj['token'] = token
    ctx.obj['course_id'] = course_id

@do_action.command(help="Export Canvas user id of active students")
@click.option('--output', default=default_enrollments_export_file, help="Output file. Default is {}".format(default_enrollments_export_file))
@click.pass_context
def export(ctx, output):
    token = ctx.obj['token']
    course_id = ctx.obj['course_id']

    # only include enrolled active students
    export_course_active_enrollments(token, course_id, output)
    print('Active student enrollments exported to "{}"'.format(output))

@do_action.command(help="Send conversations based on given template and values")
@click.option('--template', default=default_template_file, help="Template file for the conversation. Default is {}".format(default_template_file))
@click.option('--values', default=default_conversation_values, help="CSV file of mail-merge values. Default is {}".format(default_conversation_values))
@click.pass_context
def send_conversation(ctx, template, values):
    token = ctx.obj['token']
    course_id = ctx.obj['course_id']

    merge_and_send_conversation(token, course_id, template, values)


if __name__ == "__main__": 
    do_action(obj={})
