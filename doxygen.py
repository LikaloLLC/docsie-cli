import click
from datetime import datetime, timedelta
import json
import os
import requests

# === Helper Functions ===

def date_compare(d):
    return datetime.now() >= d

def date_convert(dstr):
    datetime_object = datetime.strptime(dstr, '%Y-%m-%dT%H:%M:%S.%fZ')
    return datetime_object

def get_token():
     with open(get_login_file(), 'r') as jsonFile:
        tokens = json.load(jsonFile)
        # ...
        if date_compare(date_convert(tokens["expires"])):
          refresh()
          return get_token()
        return tokens["access_token"]

def get_refresh_token():
     with open(get_login_file(), 'r') as jsonFile:
        tokens = json.load(jsonFile)
        return tokens["refresh_token"]

def get_login_file():
    return 'docsie_login.json'

def get_conf_file():
    return 'docsie_conf.json'

def get_conf():
    # reading JSON object
    try:
        with open(get_conf_file(), 'r') as jsonFile:
            return json.load(jsonFile)
    except:
        return {}

def write_conf(conf):
    # writing JSON object
    with open(get_conf_file(), "w") as jsonFile:
        json.dump(conf, jsonFile)

def refresh():
    refreshtokens = requests.post('https://app.docsie.io/cli/refresh/',
    json={'refresh_token':get_refresh_token()})
    with open(get_login_file(), 'w') as jsonFile:  # writing JSON object
        json.dump(refreshtokens.json(), jsonFile)

# === CLI Functions ===

@click.group(chain=True)
# @click.command()
def apis():
    click.echo("Hello World")

@apis.command('login')
@click.option('--verbose','-v', count=True, help="Will print verbose messages.")
@click.option('--username','-u', prompt=True,
              default=lambda: os.environ.get('USER', ''),
              show_default='current user')
@click.option('--password','-p', prompt=True, hide_input=True,
              confirmation_prompt=False)
def apis1(verbose,username,password):
    """This is an example script to learn Click."""
    if verbose:
        click.echo("We are in the verbose mode {0}".format(verbose))
    click.echo("Hello World")
    click.echo('We received {0} as password.'.format(password))
    print("Hello,", username)

    tokens = requests.post('https://app.docsie.io/cli/login/', 
        json={'username': username, 'password': password})
    print(tokens)
    print(tokens.text)
    with open(get_login_file(), 'w') as jsonFile:  # writing JSON object
        json.dump(tokens.json(), jsonFile)


@apis.command('list')
def apis2():
    click.echo('Bye Bye Bye')

    shelfs = requests.get('https://app.docsie.io/cli/shelfs/', 
        headers={'Authorization':get_token()})
    counter = 0
    for i in shelfs.json():
        counter +=1
        #print(i)
        print(counter,i["name"])

@apis.command('select')
def apis3():
    click.echo('Hey Hey Hey')
    shelfs = requests.get('https://app.docsie.io/cli/shelfs/',
        headers={'Authorization':get_token()})
    counter = 0
    for i in shelfs.json():
        counter +=1
        #print(i)
        print(counter,i["name"])

    inp = int(input("Which shelf? "))
    while not (inp > 0 and inp <= counter):
        inp = int(input("the shelf must be in range 1 - " + str(counter) + ": "))
    print(shelfs.json()[inp - 1]["id"])

    conf = get_conf()

    conf["id"] = shelfs.json()[inp - 1]["id"]

    write_conf(conf)


@apis.command('set-command')
@click.argument('command', type=click.Choice(['pydoc', 'javadoc'], case_sensitive=False))
def apis4(command):
    click.echo(command)
    conf = get_conf()
    conf['command'] = command
    write_conf(conf)
