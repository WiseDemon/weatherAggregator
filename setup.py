from setuptools import setup, find_packages

setup(
    name='weatherAggregator',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'click',
        'requests',
        'pytest',
    ],
)
