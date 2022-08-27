## Migrating from easy_my_coop* to cooperator modules

Run this command before updating your modules

.. code-block:: shell

  cat rename_deprecated_modules.py | ./odoo/odoo-bin shell -c odoo.conf --no-http  --stop-after-init -d <db-name>

## Deploying with pip

We used [odoo setup tools](https://pypi.org/project/setuptools-odoo/#packaging-a-single-addon) to generate the pypi files from the odoo manifests. To deploy any packaged module, so that odoo can later install them,
you can create a venv with this name (it's git-ignored)
```shell
python -m venv venv
```
And then pip-install them [from pypi](https://pypi.org/user/coopdevs/).

### Example

For instance, for the addon `cooperator_portal`

.. code-block:: shell

  pip install odoo14-addon-cooperator-portal==14.0.1.0.0.99.dev9

Beware that for word separation, pypi uses dashes `-` and odoo underscores `_`.
