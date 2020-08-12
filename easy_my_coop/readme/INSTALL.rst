## Deploying with pip

We used [odoo setup tools](https://pypi.org/project/setuptools-odoo/#packaging-a-single-addon) to generate the pypi files from the odoo manifests. To deploy any packaged module, so that odoo can later install them,
you can create a venv with this name (it's git-ignored)
```shell
python -m venv venv
```
And then pip-install them [from pypi](https://pypi.org/user/coopdevs/).

### Example

For instance, for the addon `easy_my_coop_website_portal`
```shell
pip install odoo12-addon-easy-my-coop-website-portal==12.0.1.0.0.99.dev9
```
Beware that for word separation, pypi uses dashes `-` and odoo underscores `_`.
