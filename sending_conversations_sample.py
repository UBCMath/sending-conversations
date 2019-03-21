# -*- coding: utf-8 -*-
"""
@author: Jeremy H. & Victor S.
"""

import requests, pandas as pd, getpass


#Canvas instance URL
url = "https://canvas.ubc.ca"

if __name__ == "__main__": 
    
    #importing Excel file and parsing into a dataframe
    the_file = pd.read_csv('key.csv')
    
    token = getpass.getpass("Enter your Canvas Token: ")
    course = input("Enter your Canvas course ID: ")
    
    print("Sending your messages...")
    for index, row in the_file.iterrows():
        recipient = str(row['User ID'])
        key = str(row['key'])
        
        #payload/contents of your API request
        payload =  {'recipients[]': [recipient],
                    'subject': "title of email",
                    'context_code': 'course_{}'.format(course),
                    'body': """
                    Dear ....
                    Body text
                    Key 1: {}\n
                    Body text
                    \n

                   """.format(key)}
        
		#Post the request
        r = requests.post('{}/api/v1/conversations'.format(url), 
                           params = payload, 
                           headers= {'Authorization': 'Bearer ' + token})
        
        if not r.ok:
            print(r.text)
            print("Failed to send message for student ID: {}. {}".format(recipient, r))

