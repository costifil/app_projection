import setuptools
from video_proj import version

setuptools.setup(
    name="Video Projection",
    version=version.__version__,
    author="CF",
    author_email="",
    description="video projection module",
    long_description="This module will play some apps on the desired screen",
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: CF License",
        "Operating System :: Windows OS",
    ],
    python_requires='>=3.9',
    install_requires=[],
    entry_points = {
        'console_scripts': ['video_projection=video_proj.video_app:main']
    },
    include_package_data=True
)