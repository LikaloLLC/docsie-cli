import click
from datetime import datetime, timedelta
import json
import os
import requests
import subprocess

# === Helper Functions ===

def date_compare(d):
    '''
    Checks to see if the date is in past
    '''
    return datetime.now() >= d

def date_convert(dstr):
    '''
    Converts the expiration date from string to datetime
    '''
    datetime_object = datetime.strptime(dstr, '%Y-%m-%dT%H:%M:%S.%fZ')
    return datetime_object

def get_docid(ctx):
    '''
    Gets the document id from config
    '''
    conf = get_conf(ctx)
    return conf['id']

def get_name(ctx):
    '''
    Gets the name from config
    '''
    conf = get_conf(ctx)
    return conf['name']

def get_description(ctx):
    '''
    Gets the description from config
    '''
    conf = get_conf(ctx)
    return conf['description']

def get_tags(ctx):
    '''
    Gets tags from config
    '''
    conf = get_conf(ctx)
    return conf['tags']

def get_token(ctx):
    '''
    Reads a login file and retuns the access token
    '''
    with open(get_login_file(ctx), 'r') as jsonFile:
        tokens = json.load(jsonFile)
        # Check to see if the token is expired
        if date_compare(date_convert(tokens["expires"])):
            # Refresh the expired token
            refresh(ctx)
            return get_token(ctx)
        return tokens["access_token"]
 
def get_refresh_token(ctx):
    '''
    Reads the login file and returns a refresh token
    '''
    with open(get_login_file(ctx), 'r') as jsonFile:
        tokens = json.load(jsonFile)
        return tokens["refresh_token"]

def get_login_file(ctx):
    '''
    Returns the name for the login file (default: `docsie_login.json`)
    '''
    if 'login' in ctx.obj:
        if ctx.obj['login']:
            return ctx.obj['login']
    return 'docsie_login.json'

def get_conf_file(ctx):
    '''
    Returns the name for the config file (default: `docsie_conf.json`)
    '''
    if 'config' in ctx.obj:
        if ctx.obj['config']:
            return ctx.obj['config']
    return 'docsie_conf.json'

def get_conf(ctx):
    '''
    Convert the config file to config object
    '''
    # reading the JSON object
    try:
        with open(get_conf_file(ctx), 'r') as jsonFile:
            return json.load(jsonFile)
    except:
        # return empty dic when file is not found
        return {}

def write_conf(ctx, conf):
    '''
    Writing the config file
    '''
    # writing JSON object
    with open(get_conf_file(ctx), "w") as jsonFile:
        json.dump(conf, jsonFile)

def refresh(ctx):
    '''
    Refreshes tokens
    '''
    refreshtokens = requests.post('https://app.docsie.io/cli/refresh/',
    json={'refresh_token':get_refresh_token(ctx)})
    with open(get_login_file(ctx), 'w') as jsonFile:  # writing JSON object
        json.dump(refreshtokens.json(), jsonFile)


def run_pydoc(ctx):
    '''
    Runs pydoc to generate documentation
    user should set an input file in config (`file`)

    WARNING: pydoc will overwrite an html file with the same name

    '''
    conf = get_conf(ctx)
    if "file" not in conf:
        raise Exception("File not set")
    subprocess.run(["python", "-m", "pydoc", "-w", conf['file']])
    f_name = conf['file']
    if f_name.endswith('.py'):
        f_name = f_name[:-3]
    f_name = f_name + '.html'
    return f_name
 
def run_javadoc(ctx):
    '''
    Runs javadoc to generate documetation
    user should set a file name and destination (`file` ,`dest`)
    '''
    conf = get_conf(ctx)
    if "file" not in conf:
        raise Exception("File not set")
    if "dest" not in conf:
        raise Exception("enter destination on your config")
    subprocess.run(["javadoc", conf['file'], "-d", conf['dest']])
    f_name = conf['file'][:-5] + '.html'
    return f_name

def run(ctx):
    '''
    Runs the appropriate function based on the `command` config
    '''
    conf = get_conf(ctx)
    if "command" not in conf:
        raise Exception("Command not set")
    if conf["command"] == "pydoc":
        return run_pydoc(ctx)
    if conf["command"] == "javadoc":
        return run_javadoc(ctx)

# === CLI Functions ===

@click.group(chain=True)
@click.pass_context
@click.option('--config', type=click.Path(exists=False))
@click.option('--login', type=click.Path(exists=False))
def apis(ctx, config, login):
    '''
    This is the main function for click command
    '''
    ctx.ensure_object(dict)
    ctx.obj['config'] = config
    ctx.obj['login'] = login


@apis.command('login')
@click.pass_context
@click.option('--username','-u', prompt=True,
              default=lambda: os.environ.get('USER', ''),
              show_default='current user')
@click.option('--password','-p', prompt=True, hide_input=True,
              confirmation_prompt=False)
def apis1(ctx,username,password):
    '''
    Logs in to docsie and stores the tokens
    '''
    tokens = requests.post('https://app.docsie.io/cli/login/', 
        json={'username': username, 'password': password})

    with open(get_login_file(ctx), 'w') as jsonFile:  # writing JSON object
        json.dump(tokens.json(), jsonFile)


@apis.command('list')
@click.pass_context
def apis_list(ctx):
    '''
    List name of Shelves
    '''
    shelfs = requests.get('https://app.docsie.io/cli/shelfs/', 
        headers={'Authorization':get_token(ctx)})
    counter = 0
    for i in shelfs.json():
        counter +=1
        print(counter,i["name"])


@apis.command('select')
@click.pass_context
def apis_select(ctx):
    '''
    Select one of shelves
    '''
    shelfs = requests.get('https://app.docsie.io/cli/shelfs/',
        headers={'Authorization':get_token(ctx)})
    counter = 0
    shelfs = shelfs.json()

    # Print the shelves
    for i in shelfs:
        counter +=1
        print(counter,i["name"])

    inp = int(input("Which shelf? "))
    while not (inp > 0 and inp <= counter):
        inp = int(input("the shelf must be in range 1 - " + str(counter) + ": "))
    print(shelfs[inp - 1]["id"])

    conf = get_conf(ctx)

    # Update config

    conf["id"] = shelfs[inp - 1]["id"]
    conf["name"] = shelfs[inp - 1]["name"]
    conf["description"] = shelfs[inp - 1]["description"]
    conf["tags"] = shelfs[inp - 1]["tags"]

    write_conf(ctx, conf)


@apis.command('set-command')
@click.pass_context
@click.argument('command', type=click.Choice(['pydoc', 'javadoc'], case_sensitive=False))
def apis_command(ctx,command):
    '''
    Choose the generator
    '''
    click.echo(command)
    conf = get_conf(ctx)
    conf['command'] = command
    write_conf(ctx, conf)


@apis.command('set-file')
@click.pass_context
@click.argument('file', type=click.Path(exists=True))
def apis_file(ctx,file):
    '''
    Set the file
    '''
    # Adding path to avoid errors from generators
    if not file.startswith('/') and not file.startswith('./'):
        file = './' + file
    click.echo(click.format_filename(file))
    conf = get_conf(ctx)
    conf['file'] = file
    write_conf(ctx, conf)


@apis.command('update')
@click.pass_context
def apis_update(ctx):
    '''
    Updates the documents and publish to docsie.io
    '''
    f_name = run(ctx)
    with open(f_name, 'r') as f:
        # Read the generated HTML
        data = f.read()
        # Parse it for docsie
        data = requests.post('https://us-central1-docsie-io.cloudfunctions.net/DOCSIE_CONVERT', json={'html': data})
        doc_id = get_docid(ctx)
        # Publish to docsie.io
        result = requests.post('https://app.docsie.io/cli/publish/'+ doc_id+'/', json={
            'doc': data.json(),
            'name':get_name(ctx),
            'description': get_description(ctx),
            'tags': get_tags(ctx)
        }, headers={'Authorization': get_token(ctx)})
