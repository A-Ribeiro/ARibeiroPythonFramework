import setuptools
 
with open("README.md", "r") as fh:
    long_description = fh.read()

print("\n\nExporting packages:", setuptools.find_packages(),"\n\n")


setuptools.setup(
    name="aRibeiro",
    version="0.0.1",
    author="Alessandro Ribeiro, Alysson Ribeiro",
    #author_email="email@email.com",
    description="Package to create aRibeiro",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license='MIT',
    install_requires=[
        'libglfw3-dev', 'libglfw3','numpy','PyOpenGL', 'PyOpenGL_accelerate', 'glfw', 'Pillow'
    ],
    python_requires='>=3.7',
)