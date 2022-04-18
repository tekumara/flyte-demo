from pathlib import Path

from setuptools import find_packages, setup

long_description = Path("README.md").read_text()

setup(
    name="aircraft",
    version="0.0.0",
    description="aircraft etl example using Flyte",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    packages=find_packages(exclude=["tests"]),
    package_data={
        "": ["py.typed"],
    },
    install_requires=["sqlalchemy==1.4.22", "flytekit~=0.32"],
    extras_require={
        "dev": [
            "black==21.7b0",
            "isort==5.9.3",
            "flake8==3.9.2",
            "flake8-annotations==2.6.2",
            "flake8-colors==0.1.9",
            "pre-commit==2.14.0",
            "pytest==6.2.4",
        ]
    },
)
