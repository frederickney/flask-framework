# coding: utf-8


import setuptools

requirements = []


def _load_requirements(filename:str):
    requirements_fd = open(filename, "r") 
    for line in requirements_fd:
        requirements.append(line.rstrip())
    return


_load_requirements("requirements.txt") 
_load_requirements("extensions.txt")
namespaces = setuptools.find_namespace_packages(where="src")
with open("readme.md", "r") as fh:
    long_description = fh.read()
    setuptools.setup(
        name="flask_framework",
        version="1.0.0",
        author="Frédérick NEY",
        author_email="frederick.ney@gmail.com",
        description="A MVC framework for flask",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/frederickney/flask-framework",
        packages=namespaces,
        package_dir={'': 'src'},
        install_requires=requirements
    )
