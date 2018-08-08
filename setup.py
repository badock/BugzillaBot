from setuptools import setup, find_packages
setup(name='bugzillabot',
      version='0.1',
      description='A bot that simplifies discussions involving Bugzilla on mattermost',
      author='Jonathan Pastor',
      author_email='jonathan.pastor@me.com',
      license='',
      packages=find_packages(),
      install_requires=[
        'mmpy-bot',
        'urllib3',
        'requests'
      ],
      entry_points = {
          'console_scripts': ['bugzillabot=bugzillabot.command_line:main'],
          },
      zip_safe=False)
