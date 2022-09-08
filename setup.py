import setuptools

setuptools.setup(
    name='remixProject',
    version=setuptools.__version__.get_full_version(),
    packages=['spleeter', 'validators', 'youtube_dl'],
    url='https://github.com/Engineering-Final-Project/remix-project.git',
    author='harelassayag, miriamsas',
    author_email='harel.assayag@mail.huji.ac.il, miriam.sasson@mail.huji.ac.il',
    description='Remix software'
)

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# setuptools.setup(
#     name="example-pkg-YOUR-USERNAME-HERE",
#     version="0.0.1",
#     author="Example Author",
#     author_email="author@example.com",
#     description="A small example package",
#     long_description=long_description,
#     long_description_content_type="text/markdown",
#     url="https://github.com/pypa/sampleproject",
#     project_urls={
#         "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
#     },
#     classifiers=[
#         "Programming Language :: Python :: 3",
#         "License :: OSI Approved :: MIT License",
#         "Operating System :: OS Independent",
#     ],
#     package_dir={"": "src"},
#     packages=setuptools.find_packages(where="src"),
#     python_requires=">=3.6",
# )