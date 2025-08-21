from setuptools import setup, find_packages
setup(
    name="CodeFileExecutorLib",
    version="1.1.0",
    description="A Python library for batch file and folder operations with structured task definitions",
    author="Tery Tsui",
    author_email="teryfly@qq.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.8",
)