import click
import os
import requests
import json


@click.group(chain=True)
@click.command('login')
def apis():
    click.echo("Hello World")

@click.command()
@click.option('--verbose','-v', count=True, help="Will print verbose messages.")
@click.option('--username','-u', prompt=True,
              default=lambda: os.environ.get('USER', ''),
              show_default='current user')
@click.option('--password','-p', prompt=True, hide_input=True,
              confirmation_prompt=False)
def apis(verbose,username,password):
    """This is an example script to learn Click."""
    if verbose:
        click.echo("We are in the verbose mode {0}".format(verbose))
    click.echo("Hello World")
    click.echo('We received {0} as password.'.format(password))
    print("Hello,", username)

    tokens = requests.post('https://app.docsie.io/cli/login/', json={'username': username, 'password': password})
    print(tokens)
    print(tokens.text)
    with open('docsie.json', 'w') as f:  # writing JSON object
        json.dump(tokens.json(), f)