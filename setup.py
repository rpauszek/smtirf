import setuptools

with open("README.md", "r", encoding="utf-8") as F:
    long_description = F.read()

setuptools.setup(
    name="smtirf",
    version="0.2.0",
    author="Ray Pauszek, Ph.D.",
    description="Data analysis for single-molecule TIRF microscopy.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rpauszek/smtirf",
    license="BSD-2",
    packages=setuptools.find_packages(),
    python_requires=">=3.10,<3.11",
    install_requires=[
        "black",
        "pytest>=3.5",
        "h5py>=3.0, <4",
        "numpy>=1.20, <2",
        "scipy>=1.1, <2",
        "matplotlib>=3.5",
        "numba",
        "scikit-learn>=0.18.0",
        "scikit-image>=0.17.2",
        "PyQt6",
    ],
)
