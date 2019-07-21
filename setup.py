from setuptools import setup, find_packages


setup(
    name="smb3foundry",
    version="0.1.0",
    description=("SMB3 world/level editor"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="smb3 nes foundry smb3-foundry",
    author="Michael Nix",
    author_email="mchl.nix@googlemail.com",
    license="LICENSE",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=["wxPython"],
    entry_points=dict(console_scripts=["smb3foundry=smb3foundry.smb3foundry:main"]),
)
