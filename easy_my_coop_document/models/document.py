# -*- coding: utf-8 -*-

# Copyright 2018 Rémy Taymans <remytaymans@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from openerp import models, fields, api


class Document(models.Model):
    _name = 'easy_my_coop.document'
    _description = "Document"
    _order = 'document_date desc, name'

    name = fields.Char("Name", required=True)
    description = fields.Text("Description")
    document = fields.Binary('Document', attachment=True, required=True)
    filename = fields.Char("Document File Name")
    mimetype = fields.Char("Mime-Type", compute='_mimetype')
    file_size = fields.Integer("File Size", compute='_file_size')
    document_date = fields.Date("Document Date",
                                default=fields.Date.today())
    category = fields.Many2one('easy_my_coop.document.category',
                               string="Category")
    published = fields.Boolean("Published?")
    publication_date = fields.Datetime("Publication Date",
                                       compute='_publication_date',
                                       store=True)
    public = fields.Boolean("Public?")

    @api.depends('document')
    def _mimetype(self):
        for doc in self:
            attachment_mgr = self.env['ir.attachment'].sudo()
            attachment = attachment_mgr.search_read(
                [('res_model', '=', self._name),
                 ('res_id', '=', doc.id),
                 ('res_field', '=', 'document')],
                fields=['mimetype', 'file_size'],
                limit=1,
            )[0]
            doc.mimetype = attachment['mimetype']

    @api.depends('document')
    def _file_size(self):
        for doc in self:
            attachment_mgr = self.env['ir.attachment'].sudo()
            attachment = attachment_mgr.search_read(
                [('res_model', '=', self._name),
                 ('res_id', '=', doc.id),
                 ('res_field', '=', 'document')],
                fields=['mimetype', 'file_size'],
                limit=1,
            )[0]
            doc.file_size = attachment['file_size']

    @api.depends('published')
    def _publication_date(self):
        for doc in self:
            if doc.published and not doc.publication_date:
                doc.publication_date = fields.Datetime.now()
            if not doc.published:
                doc.publication_date = False


class Category(models.Model):
    _name = 'easy_my_coop.document.category'
    _description = "Category"
    _order = 'name'

    name = fields.Char("Name", required=True)
    description = fields.Text("Description")
    parent_id = fields.Many2one('easy_my_coop.document.category',
                                string="Parent Category")
    child_ids = fields.One2many('easy_my_coop.document.category',
                                'parent_id',
                                string="Child Categories")
    document_ids = fields.One2many('easy_my_coop.document',
                                   'category',
                                   string="Documents")
