"""Setup for ChatAgent XBlock."""

import os
from setuptools import setup


def package_data(pkg, roots):
    """Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.

    Arguments:
        pkg
        roots

    Returns:
        Dict:

    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='chatagent-xblock',
    version='0.1',
    author='Knut Lucas Andersen',
    description='ChatBot for answering questions related to programming by using StackOverflow as knowledge base',
    packages=[
        'chatagent',
    ],
    install_requires=[
        'XBlock',
        'Py-StackExchange'
    ],
    entry_points={
        'xblock.v1': [
            'chatagent = chatagent:ChatAgentXBlock',
        ]
    },
    package_data=package_data("chatagent", ["static", "public"]),
)
