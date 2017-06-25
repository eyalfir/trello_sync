from setuptools import setup

setup(name='trello_sync',
      version='0.2.2',
      description='simple trello board to YAML back-and-forth sync',
      author='Eyal Firstenberg',
      author_email='eyalfir@gmail.com',
      classifiers=['Development Status :: 3 - Alpha'],
      packages=['trello_sync'],
      install_requires=['trello>=0.9.1'],
      scripts=['bin/trello_sync'])
