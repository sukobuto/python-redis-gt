from setuptools import setup

requires = [
    'redis>=2.10.6',
]

with open('README.md') as f:
    long_description = f.read()

setup(
    name='redis_gt',
    version='1.0.0',
    description='Global throttling with Redis.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/sukobuto/python-redis-gt',
    author='sukobuto',
    author_email='sukobuto@gmail.com',
    license='MIT',
    keywords='throttle redis async',
    packages=[
        'redis_gt',
    ],
    install_requires=requires,
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
