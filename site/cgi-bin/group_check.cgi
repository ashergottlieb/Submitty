#!/usr/bin/env python3

"""
This script is called via GET passing in base_path and head_instructor and it checks if the head_instructor is in the group that base_path belongs to.

It returns a JSON object. A success JSON response indicates the head_instructor belongs to the group of base_path.
"""

import cgi
import json
import grp
from pathlib import Path

print("Content-type: text/html")
print()

arguments = cgi.FieldStorage()
status = 'fail'

group_name = arguments.getvalue('group_name', None)
head_instructor = arguments.getvalue('head_instructor', None)

group_mandatory_users = ['submitty_php', 'submitty_daemon', 'submitty_cgi'];

for member in grp.getgrnam(group_name).gr_mem:
    if member in group_mandatory_users:
        group_mandatory_users.remove(member)

if len(group_mandatory_users) is not 0:
    status = 'error'

if group_name and head_instructor:
    if head_instructor in grp.getgrnam(group_name).gr_mem and len(group_mandatory_users) is 0:
        status = 'success'

print(json.dumps({ "status": status }))
