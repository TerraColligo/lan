# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare

class SaleOrderSample(models.Model):
    _name = "sale.order.sample"
    _description = "Sales Samples"

    sequence = fields.Integer(string="Sequence")
    name = fields.Char(string="Barcode")
    client_communication_name = fields.Char(string="Client Communication Name")
    delivery_check = fields.Boolean(string="Delivery Check")
    lab_check = fields.Boolean(string="Lab Check")
    forced_by_client = fields.Boolean(string="Forced By Client")
    product_id = fields.Many2one('product.product', string="Sample Name")
    uom_id = fields.Many2one('uom.uom', string="UOM")
    sale_id = fields.Many2one('sale.order', string="Sale")
    sale_line_id = fields.Many2one('sale.order.line', string="Order Test")


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sample_ids = fields.One2many('sale.order.sample', 'sale_id', string="Samples", copy=False)
    is_payment = fields.Boolean(string="Payment")
    datas = fields.Binary(string="Upload Image")
    datas_fname = fields.Char(string="Filename")

    @api.multi
    def generate_samples(self):
        self.ensure_one()
        for line in self.order_line:
            if line.id not in self.sample_ids.mapped('sale_line_id').ids:
                count = (max(self.sample_ids.mapped('sequence'))) + 1 if self.sample_ids.mapped('sequence') else 1
                while len(str(count)) != 3:
                    count = '0' + str(count)
                sample_id = self.env['sale.order.sample'].create({
                        'name': self.name + '-' + str(count),
                        'product_id': line.product_id.id,
                        'client_communication_name': '',
                        'sale_line_id': line.id,
                        'uom_id': line.product_id.uom_id.id,
                        'sale_id': self.id,
                        'sequence': int(count)
                    })