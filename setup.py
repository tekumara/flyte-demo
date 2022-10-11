from setuptools import find_packages, setup

setup(
    name="aircraft",
    version="0.0.0",
    description="aircraft etl example using Flyte",
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    packages=find_packages(exclude=["tests"]),
    package_data={
        "": ["py.typed"],
    },
    install_requires=["sqlalchemy~=1.4.41", "flytekit~=1.2.1"],
    extras_require={
        "dev": [
            "black~=22.10",
            "isort~=5.10",
            "flake8~=5.0",
            "flake8-annotations~=2.9",
            "flake8-colors~=0.1",
            "pre-commit~=2.20",
            "pytest~=7.1",
        ]
    },
)
