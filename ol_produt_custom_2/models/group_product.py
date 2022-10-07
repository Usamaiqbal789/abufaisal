from odoo import models, fields,api, _
from odoo.exceptions import UserError
import base64
import requests
import datetime
from odoo.exceptions import ValidationError




class InheritProductproductgrp(models.Model):
    _inherit = 'product.product'

    attachment_ids = fields.Many2many('ir.attachment',
                                      string='Files')
    group_product_ids = fields.One2many('groups.product','grp_product_id')

    # @api.onchange('group_product_ids','group_product_ids.grp_id')
    # def set_domain_sub_grp(self):
    #
    #     # self.sub_grp_id = False
    #     if self.group_product_ids.grp_id:
    #         return {'domain': {'sub_grp_id': [('grp_id', '=', self.group_product_ids.grp_id.id)]}}
    #
    #     else:
    #         # remove the domain if no grp is selected
    #         return {'domain': {'sub_grp_id': []}}
    #
    # @api.onchange('group_product_ids','group_product_ids.sub_grp_id')
    # def set_domain_sub_sub_grp(self):
    #
    #     # self.sub_grp_id = False
    #     if self.sub_grp_id:
    #         return {'domain': {'sub_sub_grp_id': [('sub_grp_id', 'in', self.group_product_ids.sub_grp_id.id)]}}
    #
    #     else:
    #         # remove the domain if no contrat is selected
    #         return {'domain': {'sub_sub_grp_id': []}}








class GroupProduct(models.Model):
    _name = 'groups.product'

    grp_product_id =fields.Many2one('product.product')
    grp_id =fields.Many2one('brand.custom')
    sub_grp_id =fields.Many2one('sub.group.custom')
    sub_sub_grp_id =fields.Many2one('sub.sub.group.custom')

    @api.onchange('grp_id')
    def set_domain_sub_grp(self):

        # self.sub_grp_id = False
        if self.grp_id:
            return {'domain': {'sub_grp_id': [('grp_id', 'in', self.grp_id.ids)]}}

        else:
            # remove the domain if no grp is selected
            return {'domain': {'sub_grp_id': []}}

    @api.onchange('sub_grp_id')
    def set_domain_sub_sub_grp(self):

        # self.sub_grp_id = False
        if self.sub_grp_id:
            return {'domain': {'sub_sub_grp_id': [('sub_grp_id', 'in', self.sub_grp_id.ids)]}}

        else:
            # remove the domain if no contrat is selected
            return {'domain': {'sub_sub_grp_id': []}}



