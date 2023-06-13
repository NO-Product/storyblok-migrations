from setuptools import setup

setup(
    name='storyblok-migrations',
    url='https://github.com/NO-Product/storyblok-migrations',
    author='Nour Nasser',
    author_email='nour02345@gmail.com',
    packages=['storyblok_migrations'],
    install_requires=["requests"],
    version='0.1',
    license='MIT',
    description='Python library that automates the migration of content type schemas between Storyblok Spaces.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)