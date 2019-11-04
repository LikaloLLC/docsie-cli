import click
from datetime import datetime, timedelta
import json
import os
import requests
import subprocess

# === Helper Functions ===

def date_compare(d):
    return datetime.now() >= d

def date_convert(dstr):
    datetime_object = datetime.strptime(dstr, '%Y-%m-%dT%H:%M:%S.%fZ')
    return datetime_object

def get_token(ctx):
     with open(get_login_file(ctx), 'r') as jsonFile:
        tokens = json.load(jsonFile)
        # ...
        if date_compare(date_convert(tokens["expires"])):
          refresh(ctx)
          return get_token(ctx)
        return tokens["access_token"]

def get_refresh_token(ctx):
     with open(get_login_file(ctx), 'r') as jsonFile:
        tokens = json.load(jsonFile)
        return tokens["refresh_token"]

def get_login_file(ctx):
    if 'login' in ctx.obj:
        if ctx.obj['login']:
            return ctx.obj['login']
    return 'docsie_login.json'

def get_conf_file(ctx):
    if 'config' in ctx.obj:
        if ctx.obj['config']:
            return ctx.obj['config']
    return 'docsie_conf.json'

def get_conf(ctx):
    # reading JSON object
    try:
        with open(get_conf_file(ctx), 'r') as jsonFile:
            return json.load(jsonFile)
    except:
        return {}

def write_conf(ctx, conf):
    # writing JSON object
    with open(get_conf_file(ctx), "w") as jsonFile:
        json.dump(conf, jsonFile)

def refresh(ctx):
    refreshtokens = requests.post('https://app.docsie.io/cli/refresh/',
    json={'refresh_token':get_refresh_token(ctx)})
    with open(get_login_file(ctx), 'w') as jsonFile:  # writing JSON object
        json.dump(refreshtokens.json(), jsonFile)

def run_pydoc(ctx):
    conf = get_conf(ctx)
    subprocess.run(["python", "-m", "pydoc", "-w", conf['file']])

def run_javadoc(ctx):
    conf = get_conf(ctx)
    if "dest" not in conf:
        raise Exception("enter destination on your config")
    subprocess.run(["javadoc", conf['file'], "-d", conf['dest']])
    f_name = conf['file'][:-5] + '.html'
    return f_name

def run(ctx):
    conf = get_conf(ctx)
    if conf["command"] == "pydoc":
        run_pydoc(ctx)
    if conf["command"] == "javadoc":
        run_javadoc(ctx)

# === CLI Functions ===

@click.group(chain=True)
@click.pass_context
@click.option('--config', type=click.Path(exists=False))
@click.option('--login', type=click.Path(exists=False))
# @click.command()
def apis(ctx, config, login):
    click.echo("Hello World")
    ctx.ensure_object(dict)
    ctx.obj['config'] = config
    ctx.obj['login'] = login

@apis.command('login')
@click.pass_context
@click.option('--verbose','-v', count=True, help="Will print verbose messages.")
@click.option('--username','-u', prompt=True,
              default=lambda: os.environ.get('USER', ''),
              show_default='current user')
@click.option('--password','-p', prompt=True, hide_input=True,
              confirmation_prompt=False)
def apis1(ctx,verbose,username,password):
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
    with open(get_login_file(ctx), 'w') as jsonFile:  # writing JSON object
        json.dump(tokens.json(), jsonFile)


@apis.command('list')
@click.pass_context
def apis_list(ctx):
    click.echo('Bye Bye Bye')

    shelfs = requests.get('https://app.docsie.io/cli/shelfs/', 
        headers={'Authorization':get_token(ctx)})
    counter = 0
    for i in shelfs.json():
        counter +=1
        #print(i)
        print(counter,i["name"])


@apis.command('select')
@click.pass_context
def apis_select(ctx):
    click.echo('Hey Hey Hey')
    shelfs = requests.get('https://app.docsie.io/cli/shelfs/',
        headers={'Authorization':get_token(ctx)})
    counter = 0
    for i in shelfs.json():
        counter +=1
        #print(i)
        print(counter,i["name"])

    inp = int(input("Which shelf? "))
    while not (inp > 0 and inp <= counter):
        inp = int(input("the shelf must be in range 1 - " + str(counter) + ": "))
    print(shelfs.json()[inp - 1]["id"])

    conf = get_conf(ctx)

    conf["id"] = shelfs.json()[inp - 1]["id"]

    write_conf(ctx, conf)


@apis.command('set-command')
@click.pass_context
@click.argument('command', type=click.Choice(['pydoc', 'javadoc'], case_sensitive=False))
def apis_command(ctx,command):
    click.echo(command)
    conf = get_conf(ctx)
    conf['command'] = command
    write_conf(ctx, conf)


@apis.command('set-file')
@click.pass_context
@click.argument('file', type=click.Path(exists=True))
def apis_file(ctx,file):
    if not file.startswith('/') and not file.startswith('./'):
        file = './' + file
    click.echo(click.format_filename(file))
    conf = get_conf(ctx)
    conf['file'] = file
    write_conf(ctx, conf)


@apis.command('update')
@click.pass_context
def apis_update(ctx):
    run(ctx)