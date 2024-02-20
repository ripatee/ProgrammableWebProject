from setuptools import find_packages, setup

# Borrowed directly from lovelace materials

setup(
    name="MokkiWahti",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "flask",
        "flask-caching",
        "flask-restful",
        "flask-sqlalchemy",
        "jsonschema",
        "rfc3339-validator",
        "SQLAlchemy",
    ]
)
