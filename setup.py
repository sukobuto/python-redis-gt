from setuptools import setup

requires = [
    'redis>=2.10.6',
]

setup(
    name='redis_gt',
    version='1.0',
    description='Global throttling with Redis.',
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
    ],
)
