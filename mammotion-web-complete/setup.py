from setuptools import setup, find_packages

setup(
    name="mammotion-web",
    version="1.0.0",
    description="Web-based control interface for Mammotion robotic lawn mowers",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "jinja2>=3.1.2",
        "python-multipart>=0.0.6",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "pymammotion>=0.5.14",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "aiofiles>=23.2.1",
        "redis>=5.0.1",
        "structlog>=23.2.0",
        "websockets>=12.0",
    ],
    entry_points={
        "console_scripts": [
            "mammotion-web=mammotion_web.main:main",
        ],
    },
)
