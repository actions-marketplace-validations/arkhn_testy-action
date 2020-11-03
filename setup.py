from setuptools import find_namespace_packages, setup

with open("README.md") as f:
    readme = f.read()

extras_require = {"test": [], "dev": []}

setup(
    name="arkhn.testy-action",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src"),
    url="https://github.com/Arkhn/testy-action",
    license="",
    author="Valentin Matton",
    author_email="valentin@arkhn.com",
    description="GitHub Action to run Arkhn's integration test suite",
    long_description=readme,
    install_requires=["requests>=2.24,<3", "ansible-runner>=1.4,<2"],
    extras_require=extras_require,
    python_requires=">=3.8.*, <4",
    entry_points={"console_scripts": ["testy-action=arkhn.testy_action.main:main"]},
)
