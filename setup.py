import setuptools

requirements = []

def _load_requirements(filename:str):
    requirements_fd = open(filename, "r") 
    for line in requirements_fd:
        requirements.append(line.rstrip())
    return

_load_requirements("requirements.txt") 
_load_requirements("extensions.txt")


with open("readme.md", "r") as fh:
    long_description = fh.read()
    setuptools.setup(
        name = "Flask-Framework",
        version = "0.1.5",
        author = "Frédérick NEY",
        author_email = "frederick.ney@gmail.com",
        description = "A MVC framework for flask",
        long_description = long_description,
        long_description_content_type = "text/markdown",
        url = "https://github.com/frederickney/flask-framework",
        packages=setuptools.find_packages(),
        install_requires  = requirements
    )
