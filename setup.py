from setuptools import setup

setup(name='trello_sync',
      version='0.1.BUILD',
      description='simple trello board to YAML back-and-forth sync',
      author='Eyal Firstenberg',
      author_email='eyalfir@gmail.com',
      classifiers=[
                   'Development Status :: 3 - Alpha'],
      install_requires=['trello>=0.9.1'],
      package_data={'lc_ravello': ['lc_ravello_key.pem', 'lc_ravello_key.pub']},
      scripts=['bin/trello_sync.py'])
