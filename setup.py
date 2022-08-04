from setuptools import setup

setup(
    name='SQLWrapper',
    version='0.0.4',
    description='SQLWrapper object',
    author='Duke LeTran',
    author_email='daletran@ucdavis.edu',
    url='https://gitlab.ri.ucdavis.edu/ri/SQLWrapper',
    py_modules=['SQLWrapper','prompter'],
    install_requires=['pandas', 'numpy', 'pyodbc', 'sqlalchemy', 'cx-oracle'],
    license='GPLv3'
)
