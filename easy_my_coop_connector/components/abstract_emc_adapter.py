# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from urllib.parse import urljoin


class AbstractEMCAdapter:
    _model = "set in implementation class"
    _root = "/api/"
    _service = "set in implementation class"

    def __init__(self, backend, record=None):
        self.backend = backend
        self.record = record

    def _get_url(self, args=None):
        """args is a list of path elements
        :return the complete route to the service
        """
        if args is None:
            args = []
        return urljoin(self._root, self._service, *args)

    def search(self, **params):
        raise NotImplementedError

    def read(self, id_):
        # pylint: disable=method-required-super
        url = self._get_url([str(id_)])
        api_dict = self.backend.http_get_content(url)
        return self.to_write_values(api_dict)

    def create(self, record):
        # pylint: disable=method-required-super
        url = self._get_url()
        api_dict = self.to_api_dict(record)
        external_record = self.backend.http_post_content(url, api_dict)
        external_id, writeable_dict = self.to_write_values(external_record)
        return external_id, writeable_dict

    def update(self, data):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def to_write_values(self, api_dict):
        """
        :return a tuple with
            - the external id
            - a writable dictionary for _model
        received from the api
        """
        raise NotImplementedError

    def to_api_dict(self, record):
        raise NotImplementedError
