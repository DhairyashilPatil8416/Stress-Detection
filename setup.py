"""
Setup script for the StressSense Windows Agent.
"""

from setuptools import setup, find_packages

setup(
    name="windows_agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.2",
        "numpy>=1.23.5",
        "opencv-python>=4.7.0",
        # "deepface>=0.0.79",  # Removed - using custom CNN model instead
        "tensorflow>=2.14.0",  # Added for custom CNN model
        "pywin32>=305",
        "pyinstaller>=5.9.0"
    ],
    entry_points={
        'console_scripts': [
            'stresssense=windows_agent.__main__:main',
        ],
    },
)
