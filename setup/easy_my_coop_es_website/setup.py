import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        'depends_override': {
            'easy_my_coop_website': 'odoo12-addon-easy-my-coop-website>=12.0.1.0.6'
        }
    }
)
