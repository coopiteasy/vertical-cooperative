Manage cooperators of a cooperative.

A basic flow can be the following:

- Create subscription request for a person (moral or physical)
- Validate subscription request, a capital release request (an invoice: `account.move`).
  This invoice is sent to the future cooperator.
- Payment of the cooperator is registered and the capital Release
  request is marked as paid.
- A new cooperator (a special partner) is created, and the right type
  and amount of share is linked to this new cooperator.
- The new cooperator appears in the Cooperator Registry.

Features:

- Manage several share types
- Manage share subscription request
- Cooperators can be individuals or companies
- Get an up to date Cooperator Registry
- See shares of a cooperator on the partner view
- Manage departure of cooperators
- Manage conversion between different share type
- Send automatic mail to the future cooperator during the procedure
- Can be used with multi-company configuration
- Generate Cooperator Certificate and several reports about cooperators

Configurations:

- on the company, set a default payment term for the capital release requests.
- on the company, set the cooperator account.
