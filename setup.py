from setuptools import setup,find_packages

setup(
    py_modules=[],

    name="remkodrive",
    version="0.23",
    description="Sync tool for onedrive..(ALPHA!)",
    author="Remko Weingarten",
    author_email="remko66@gmail.com",
    license="GNU",
    packages=find_packages(),
    install_requires=["tendo","onedrivesdk","inotify"],
    entry_points={'console_scripts':['sapp=remkodrive.remkodrive:main']},
    data_files=['remkodrive/internal1','remkodrive/internal2','remkodrive/driveoff.ico','remkodrive/driveon.ico','remkodrive/readme']

)