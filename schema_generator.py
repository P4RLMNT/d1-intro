#!usr/bin/python

import sys
import os
import json
import re

'''

    This will parse a sample json file and create a schema based on the structure of the json object. 
    The process will work as follows:

    - Detect data type of root element. 

    - If type == object, get all property names (keys), then parse each property for its data type. 

    - If type == object repeat step above. 

    - If type == array, *assume* all elements are of same type and simply check the type of the 
      first element. 
     
    - If type == array or object, repeat steps above. 

    - If type != array or object, simply return a json object in the following format:
      {
        'type': <type>
      }


    To use this script use the following command:

    python schema_generator.py <output path> <sample json> <template>
'''


######################     Error Checking.    #########################
try:
    output_path = sys.argv[1]
except:
    print('ERROR! Output path null or missing.')

try:
    sample_path = sys.argv[2]
except:
    print('ERROR! Sample input path null or missing.')

try:
    template_path = sys.argv[3]
except:
    print('ERROR! Template input path null or missing.')


if not sample_path.endswith('.json'):
    print(f'ERROR! {sample_path.name} must be of filetype .json')
    sys.exit(0)

if not template_path.endswith('.json'):
    print(f'ERROR! {template_path.name} must be of filetype .json')
    sys.exit(0)


if not os.path.exists(output_path):
    os.makedirs(output_path)

with open(sample_path) as sample_file:
    '''Open and read sample json file'''
    sample_json = json.load(sample_file)

with open(template_path) as template_file:
    '''Open and read template json file'''

    template_json = json.load(template_file)


def get_prop_from_obj(obj, schema):
    '''Return list of object properties'''

    for key in obj.keys():
        schema['properties'][key] = get_type_from_prop(obj[key])

    return schema


def get_type_from_prop(prop):
    '''
    Return the type of json object property.

    TODO: Need to add functionality for more data types such as floats, doubles, etc.
    '''

    if isinstance(prop, str):
        return get_string_format(prop)
    if isinstance(prop, dict):
        return get_json_object_schema(prop)
    if isinstance(prop, int):
        return { 'type':'integer' }
    if isinstance(prop, list):
        return get_json_array_schema(prop)
    return { 'type':'any' }


def get_string_format(s):
    '''Return string format should the string be a date'''

    schema = { 'type':'string' }
    match = re.search(r'/\b[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\b', s)
    if match:
        schema['format'] = 'date'

    return schema


def get_json_object_schema(obj):
    '''Return schema of a json object.'''

    schema = { 'type': 'object', 'properties': {} }

    for key in obj.keys():
        schema['properties'][key] = get_type_from_prop(obj[key])

    return schema



def get_json_array_schema(arr):
    '''Return schema of a json array.'''
    
    schema = [{ 'type': 'array' }]

    schema[0]['items'] = get_type_from_prop(arr[0])

    return schema

    
def create_schema_from_sample(s, t):
    '''Return schema of a standard json element.'''

    # Get event name and replace placeholder with event name.
    eventName = s['eventName']
    t['$id'] = t['$id'].replace('###Replace_Me', eventName + '.json')
    t['title'] = t['title'].replace('###Replace_Me', eventName) 

    # Begin creating schema by getting the type of the root element of the sample message.
    t = get_prop_from_obj(s, t)

    with open(f'{eventName}_schema.json', 'w') as file:
        file.write(json.dumps(t))

    print(f'{eventName}_schema.json generated successfully.')
            

if __name__ == '__main__':
    print(f'Generating Schema for file: {sample_file.name}')
    create_schema_from_sample(sample_json, template_json)


