from setuptools import setup, find_packages

setup(
    name="petwell",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn[standard]>=0.15.0",
        "sqlalchemy>=1.4.23",
        "pytest>=6.2.5",
    ],
) 