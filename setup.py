from setuptools import find_packages, setup

DESCIPTION = "SQLAlchemy-based library that allows you to implement a uow pattern based on this library"


with open("VERSION", "r") as f:
    VERSION = f.read().strip()


with open("requirements.txt", "r") as requirements_file:
    REQUIREMENTS = requirements_file.readlines()


setup(
    name="axsqlalchemy",
    version=VERSION,
    author="axdjuraev",
    author_email="<axdjuraev@gmail.com>",
    description=DESCIPTION,
    packages=find_packages(),
    install_requires=REQUIREMENTS,
)
