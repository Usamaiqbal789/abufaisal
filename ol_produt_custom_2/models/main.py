from odoo import models, fields,api, _
from odoo.exceptions import UserError
import base64
import requests
import datetime
from odoo.exceptions import ValidationError


class image(models.Model):
    _inherit = 'product.template'

    attachment_ids = fields.Many2many('ir.attachment',
                                      string='Files')
    #
    # def multiimage(self):
    #     print("hello")




class accountmove(models.Model):
    _inherit = 'product.product'


    brand_id = fields.Many2one('brand.main.custom',  string="Brand")
    grp_id = fields.Many2one('brand.custom',  string="Group")
    sub_grp_id = fields.Many2one('sub.group.custom',  string="Sub Group")
    sub_sub_grp_id = fields.Many2one('sub.sub.group.custom',  string="Sub Sub Group")
    attachment_ids = fields.Many2many('ir.attachment',
                                      string='Files')
    oem_code = fields.Char('OEM Code')
    product_make_type = fields.Selection([('genuine', 'Genuine'), ('replacement', 'Replacement'), ('commercial', 'Commerical')],
                                               string='Product Make Type',
                                               default='')

    own_ref_no = fields.Integer('Own Reference Number')

    part_num = fields.Char('Part Number')
    part_family = fields.Selection(
        [('engine', 'Engine'), ('body', 'Body'), ('electrical', 'Electrical'), ('cooling', 'Cooling'), ('transmission', 'Transmission')],
        string='Parts Family',
        default='')
    des_arabic = fields.Char('Description in Arabic')
    min_unit_price = fields.Float('Min Unit Price')
    alternative_products = fields.Many2many(
        comodel_name='product.product',
        relation='contents_found_rel',
        column1='lot_id',
        column2='content_id',
        string='alternative Products')
    # alter_product = fields.Many2many('product.product', string='Alternative Products')

    @api.onchange('part_num')
    def check_own_ref_no_dup(self):
        check_own_ref_no = self.env['product.product'].search([('part_num', '=', self.part_num)])
        if self.part_num:
            if check_own_ref_no:
                for on in check_own_ref_no:
                    self.own_ref_no=on.own_ref_no
            else:
                last_item=self.env['product.product'].search([('own_ref_no','!=',False)],order='own_ref_no desc',limit=1)
                print(last_item)
                self.own_ref_no=last_item.own_ref_no+1




    # def create_own_ref(self):
    #     @api.model
    #     def create(self, vals):
    #         # print(vals.get('name_seq'))
    #         if vals.get('own_ref_no', _('New')) == _('New'):
    #             vals['own_ref_no'] = self.env['ir.sequence'].next_by_code('product.product') or _('New')
    #         result = super(accountmove, self).create(vals)
    #         return result

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
