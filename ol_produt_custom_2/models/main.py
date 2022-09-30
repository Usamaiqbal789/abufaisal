from email.mime import image
from odoo import models, fields,api
from odoo.exceptions import UserError
import base64
import requests
import datetime

class ProdTemp(models.Model):
    _inherit = 'product.template'
    multi_images = fields.One2many(comodel_name='product.multi.images', inverse_name='product_id', string='Multi Images')    
    

class accountmove(models.Model):
    _inherit = 'product.product'

    brand_id = fields.Many2one('brand.main.custom',  string="Brand")
    grp_id = fields.Many2one('brand.custom',  string="Group")
    sub_grp_id = fields.Many2one('sub.group.custom',  string="Sub Group")
    sub_sub_grp_id = fields.Many2one('sub.sub.group.custom',  string="Sub Sub Group")

    @api.onchange('grp_id')
    def set_domain_sub_grp(self):


        # self.sub_grp_id = False
        if self.grp_id:
            return {'domain': {'sub_grp_id': [('grp_id', '=', self.grp_id.id)]}}

        else:
            # remove the domain if no contrat is selected
            return {'domain': {'sub_grp_id': []}}

    @api.onchange('sub_grp_id')
    def set_domain_sub_sub_grp(self):

        # self.sub_grp_id = False
        if self.sub_grp_id:
            return {'domain': {'sub_sub_grp_id': [('sub_grp_id', '=', self.sub_grp_id.id)]}}

        else:
            # remove the domain if no contrat is selected
            return {'domain': {'sub_sub_grp_id': []}}




class Brandsclass(models.Model):
    _name ='brand.custom'


    name = fields.Char('Name',required=True)
    code = fields.Char('Code')
    discription = fields.Char('Discription')

class SubGroupClass(models.Model):
    _name ='sub.group.custom'


    name = fields.Char('Name',required=True)
    code = fields.Char('Code')
    discription = fields.Char('Discription')
    grp_id = fields.Many2one('brand.custom',string="Group")

class SubSubGroupClass(models.Model):
    _name ='sub.sub.group.custom'


    name = fields.Char('Name',required=True)
    code = fields.Char('Code')
    discription = fields.Char('Discription')
    sub_grp_id = fields.Many2one('sub.group.custom',string="Sub Group")
    # brand_main_ids = fields.Many2one('brand.main.custom', string="Brand ID")

class BRandClass(models.Model):
    _name ='brand.main.custom'
    name = fields.Char('Name',required=True)
    code = fields.Char('Code')
    discription = fields.Char('Discription')

class MultiImages(models.Model):
    _name='product.multi.images'
    name = fields.Char(string='Discription')
    images = fields.Binary(string='Images')
    product_id = fields.Many2one(comodel_name='product.template', string='Product ID')
    