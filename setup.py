from setuptools import setup

setup(
    name='sqlwrapper',
    version='0.0.5',
    description='SQLWrapper object',
    author='Duke LeTran',
    author_email='daletran@ucdavis.edu',
    url='https://gitlab.ri.ucdavis.edu/ri/SQLWrapper',
    py_modules=['sqlwrapper','prompter'],
    install_requires=['pandas', 'numpy', 'pyodbc', 'sqlalchemy', 'cx-oracle'],
    license='GPLv3'
)
