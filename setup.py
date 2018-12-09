from setuptools import setup

with open('VERSION') as f:
    VERSION = f.read().strip()

with open('README.md') as f:
    LONG_DESCRIPTION = f.read()

with open('requirements.txt') as f:
    INSTALL_REQUIRES = [line.strip() for line in f if line.strip()]

setup(
    name='sqlcsv',
    version=VERSION,
    license='MIT',
    description='Import/Export data to/from relational databases using SQL statements with CSV files',  # noqa
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/yubessy/sqlcsv',
    author='Shotaro Tanaka',
    author_email='yubessy0@gmail.com',
    packages=[
        'sqlcsv',
    ],
    entry_points=dict(
        console_scripts=[
            'sqlcsv=sqlcsv.cli:cli',
        ],
    ),
    install_requires=INSTALL_REQUIRES,
)
