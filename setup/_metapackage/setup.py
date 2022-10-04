import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-cooperative",
    description="Meta package for oca-cooperative Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-cooperator',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 12.0',
    ]
)
