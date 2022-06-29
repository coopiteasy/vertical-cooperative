# Copyright 2021 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

_logger = logging.getLogger(__name__)

# undefined name 'env'
env = env  # noqa: F821

module_to_uninstall_names = [
    "partner_age",
]
modules_to_uninstall = env["ir.module.module"].search(
    [
        (
            "name",
            "in",
            module_to_uninstall_names,
        ),
        ("state", "=", "installed"),
    ]
)
for module in modules_to_uninstall:
    _logger.info("uninstall %s", module.name)
    try:
        module.button_immediate_uninstall()
    except Exception:
        _logger.exception("failed to uninstall %s", module.name)
