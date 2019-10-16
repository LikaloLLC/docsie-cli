from setuptools import setup

setup(
    name="mydoxygen",
    version='0.1',
    py_modules=['doxygen'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        mydoxygen=doxygen:apis
    ''',
)