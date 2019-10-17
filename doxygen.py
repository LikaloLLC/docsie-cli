import click
import os
import requests
import json

# === Helper Functions ===

def get_token():
     with open(get_login_file(), 'r') as jsonFile:
        tokens = json.load(jsonFile)
        return tokens["access_token"]


def get_login_file():
    return 'docsie_login.json'

def get_conf_file():
    return 'docsie_conf.json'

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
    try:
        with open(get_conf_file(), 'r') as jsonFile:  # writing JSON object
            conf = json.load(jsonFile)
    except:
        conf = {}

    conf["id"] = shelfs.json()[inp - 1]["id"]

    with open(get_conf_file(), "w") as jsonFile:
        json.dump(conf, jsonFile)
