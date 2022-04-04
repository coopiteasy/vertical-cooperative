## Configuration

Get an API token from the Easy My Coop API you wish to connect to
and setup a backend at
- Settings > Technical (debug mode) > EMC Backend

## Concepts

The models are heavily influenced by the odoo connector:

- emc_backend
   - connects to the API, sends HTTP requests, converts json to dictionaries
- <model>_adapter
   - uses the backend to send query for model it's responsible for.
   - adapts the objects to api format dictionaries
   - adapts the result dictionaries to writable dictionaries
- <model>_binding
   - links an internal record with an external record for each backend

The <model> is responsible for the orchestration of these components.

In the current implementation, only one backend is allowed.
