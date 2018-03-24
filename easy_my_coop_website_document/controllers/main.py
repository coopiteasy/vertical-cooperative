# -*- coding: utf-8 -*-

# Copyright 2018 Rémy Taymans <remytaymans@gmail.com>
# Copyright 2015-2016 Odoo S.A.
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import base64

from openerp import http
from openerp.http import request, Response
from openerp.fields import Date


class DocumentWebsite(http.Controller):

    @http.route('/documents/<int:oid>', auth='public', website=True)
    def get_document(self, oid=-1):
        """Render a http response for a document"""
        document_mgr = request.env['easy_my_coop.document'].sudo()
        doc = document_mgr.browse(oid)
        ir_http_mgr = request.env['ir.http'].sudo()
        status, headers, content = ir_http_mgr.binary_content(
            model=doc._name,
            id=oid,
            field='document',
            filename_field='filename',
            download=True
        )
        if status == 304:
            return Response(status, headers)
        elif status == 301:
            # TODO: test this case not sure if this render the same
            # return werkzeug.utils.redirect(content, code=301)
            return request.redirec(content, code=301)
        elif status != 200:
            return request.not_found()
        content_base64 = base64.b64decode(content)
        headers.append(('Content-Length', len(content_base64)))
        return request.make_response(content_base64, headers)

    @http.route('/documents', auth='public', website=True)
    def template_website_document(self, date_begin=None, date_end=None, **kw):
        """
        """
        values = {}
        values.update(self.website_document_side_bar(
            date_begin=date_begin,
            date_end=date_end,
            user=request.env.user,
        ))
        values.update(self.display_categories_and_documents(
            date_begin=date_begin,
            date_end=date_end,
            user=request.env.user,
        ))
        values['size_to_str'] = self.size_to_str
        return request.render(
            'easy_my_coop_website_document.template_website_document',
            values,
        )

    def website_document_side_bar(self, date_begin=None, date_end=None,
                                  user=None):
        domains = []
        # Show only doc that are published
        domains.append(('published', '=', True))
        # Show only authorized documents
        if not self._is_authorized_user(user):
            domains.append(('public', '=', True))
        # Show only doc in the time frame
        if date_begin and date_end:
            domains.append(('document_date', '>=', date_begin))
            domains.append(('document_date', '<', date_end))
        return {
            'archive_groups': self._get_archive_groups(
                'easy_my_coop.document',
                domains,
                fields=['name', 'document_date'],
                groupby='document_date',
                order='document_date desc'),
        }

    def display_categories_and_documents(self, date_begin=None, date_end=None,
                                         user=None):
        """Prepare value for display_categories_and_documents template"""
        data = self._data_tree()
        # Show only doc that are published
        data = self._data_filter_document(
            data,
            lambda r: r.published
        )
        # Show only authorized documents
        if not self._is_authorized_user(user):
            data = self._data_filter_document(
                data,
                lambda r: r.public
            )
        # Show only doc in the time frame
        if date_begin and date_end:
            data = self._data_filter_document(
                data,
                lambda r: (r.document_date >= date_begin
                           and r.document_date < date_end)
            )
        # After all the filter, remove the empty categories
        data = self._data_remove_empty_category(data)
        return {
            'category_tree': data,
        }

    def size_to_str(self, size):
        units = ['o', 'ko', 'Mo', 'Go', 'To']
        size_float = float(size)
        for unit in units:
            if size_float < 1000:
                return '%.01f %s' % (size_float, unit)
            size_float /= 1000

    def _data_tree(self, category=None):
        """Return a tree with categories and documents in it"""
        category_mgr = request.env['easy_my_coop.document.category'].sudo()
        document_mgr = request.env['easy_my_coop.document'].sudo()
        if category:
            categories = category.child_ids.sorted(
                key=lambda r: r.name
            )
            documents = category.document_ids
        else:
            categories = category_mgr.search(
                [('parent_id', '=', False)],
                order="name"
            )
            documents = document_mgr.search(
                [('category', '=', False)]
            )
        if categories.ids:
            tree = []
            for cat in categories:
                tree.append(self._data_tree(cat))
            return (category, tree, documents)
        else:
            return (category, [], documents)

    def _data_filter_document(self, data, filter_fun):
        category, child_data, documents = data
        tree = []
        for entry in child_data:
            tree.append(
                self._data_filter_document(entry, filter_fun)
            )
        return (category, tree, documents.filtered(filter_fun))

    def _data_remove_empty_category(self, data):
        category, child_data, documents = data
        child_data = [
            self._data_remove_empty_category(c) for c in child_data
            if not self._data_is_empty(c)
        ]
        return (category, child_data, documents)

    def _data_is_empty(self, data):
        """Return True if data is empty"""
        _, child_data, documents = data
        # If there is documents, it's not empty.
        if documents.ids:
            return False
        # We are sure there is no documents.
        # If there is no child, it's empty.
        if not child_data:
            return True
        # We are sure there is childs
        for entry in child_data:
            # If a child is not empty, it's not empty
            if not self._data_is_empty(entry):
                return False
        # Else it's empty
        return True

    def _is_authorized_user(self, user=None):
        return user is not None and (user.has_group('base.group_portal')
                                     or user.has_group('base.group_user'))

    def _get_archive_groups(self, model, domain=None, fields=None,
                            groupby="create_date", order="create_date desc"):
        if not model:
            return []
        if domain is None:
            domain = []
        if fields is None:
            fields = ['name', 'create_date']
        groups = []
        for group in request.env[model].sudo().read_group(
                domain, fields=fields, groupby=groupby, orderby=order):
            label = group[groupby]
            date_begin = date_end = None
            for leaf in group["__domain"]:
                if leaf[0] == groupby:
                    if leaf[1] == ">=":
                        date_begin = leaf[2]
                    elif leaf[1] == "<":
                        date_end = leaf[2]
            groups.append({
                'date_begin': Date.to_string(Date.from_string(date_begin)),
                'date_end': Date.to_string(Date.from_string(date_end)),
                'name': label,
                'item_count': group[groupby + '_count']
            })
        return groups
