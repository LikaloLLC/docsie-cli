# docsie-cli
Generate documentation from code and import it into docsie

## Requirements

Docsie works on `python3`, and requires the libraries `click` and `requests`. In order to function properly, you need to have either `pydoc` or `javadoc` available from your shell. Other tools will be added soon.

## Installation

Install from pip: Coming Soon

To install from source code run:

```
$ git clone https://github.com/LikaloLLC/docsie-cli.git
$ cd docsie-cli
$ python setup.py install  # Or 'pip install .'
```

To install a development version, where you can see the effects of changes immediately, run:

```
$ git clone https://github.com/LikaloLLC/docsie-cli.git
$ cd docsie-cli
$ pip install -editable .
```

## Usage

The first step is initialization, go to your project directory and run:

```
docsie login
```

Enter your docsie username and password, this will create the login file for you.

Now you need to select the shelf, run:

```
docsie select
```

And follow the prompt on the screen.

Next you need to choose your command, run:

```
docsie set-command pydoc # or javadoc
```

And finally select the starting point of your project:

```
docsie set-file main.py # change with your file name
```

These configs affect the project config file.

Finally in order to upload your documentations, run 

```
docsie update
```

This will create a new notebook in the selected shelf.

## Configs

There are two configuration files, a login file and a project config file. Both of them are `json` documents and could be edited by the user.

The login file contains tokens and doesn't need to be modified by the user, it will be overwritten when the token expires.

The project config file contains the following information:

```
{
  "command": "Command to run, set by docsie set-command, javadoc or pydoc",
  "description": "Document description(uses the shelf description by default)",
  "dest": "document generated destination, needed by javadoc",
  "file": "Project entry file (set by docsie set-file)",
  "id": "Shelf id to store the documents (Set by docsie select)",
  "name": "Document name (uses the shelf name by default)",
  "tags": "Document tags (uses the shelf tags by default)"
}
```

## Flags

You can specify where to look for the login file or the config file using:

```
docsie --config PATH command
docsie --login PATH command
docsie --config PATH --login PATH command
```

## Other Commands

```
docsie list
```

Lists all available shelves for you.
