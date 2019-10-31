from setuptools import setup

setup(
    name="docsie",
    version='0.1',
    py_modules=['docsie'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        docsie=docsie:apis
    ''',
)