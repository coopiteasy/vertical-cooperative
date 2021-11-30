import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon=True,
    odoo_addons={
        'depends_override': {
            'auth_api_key': 'odoo12-addon-auth-api-key==12.0.2.1.1',
        }
    }
)
