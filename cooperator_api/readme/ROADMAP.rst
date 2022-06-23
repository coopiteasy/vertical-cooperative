The API should generate and use an external id for records instead
of odoo's generated id. It would make importing and export data as
well as migrating across versions easier.

One way would be to use uuid but the default BaseRESTController
routes would need to be rewritten: they only take integer as ids.
Another way is to define a sequence per model.
