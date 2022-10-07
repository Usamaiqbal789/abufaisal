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





class accountmove(models.Model):
    _inherit = 'product.product'



    brand_id = fields.Many2one('brand.main.custom', string="Brand")
    grp_id = fields.Many2many('brand.custom', string="Group",compute='_group_comp', store=True)
    sub_grp_id = fields.Many2many('sub.group.custom', string="Sub Group" ,compute='_sub_group_comp', store=True)
    sub_sub_grp_id = fields.Many2many('sub.sub.group.custom', string="Sub Sub Group",compute='_sub_sub_group_comp', store=True)
    product_make_type_id = fields.Many2one('product.make.type', string="Product Make Type")
    parts_family_id = fields.Many2one('parts.family',  string="Parts Family")
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
        string='Alternative Products')

    @api.depends('group_product_ids', 'group_product_ids.grp_id')
    def _group_comp(self):
        g_ids=[]
        if self.group_product_ids:
            for g in self.group_product_ids:
                if g.grp_id:
                    g_ids.append(g.grp_id.id)
            self.grp_id = [(6,0,g_ids)]
        else:
            self.grp_id = [(6, 0, [])]

    @api.depends('group_product_ids', 'group_product_ids.sub_grp_id')
    def _sub_group_comp(self):
        g_ids=[]
        if self.group_product_ids:
            for g in self.group_product_ids:
                if g.sub_grp_id:
                    # return {'domain': {'sub_grp_id': [('grp_id', 'in', self.group_product_ids.grp_id.id)]}}
                    g_ids.append(g.sub_grp_id.id)
            self.sub_grp_id = [(6,0,g_ids)]
        else:
            self.sub_grp_id = [(6, 0, [])]

    @api.depends('group_product_ids', 'group_product_ids.sub_sub_grp_id')
    def _sub_sub_group_comp(self):
        g_ids=[]
        if self.group_product_ids:
            for g in self.group_product_ids:
                if g.sub_sub_grp_id:
                    # return {'domain': {'sub_sub_grp_id': [('sub_grp_id', 'in', self.group_product_ids.sub_grp_id.id)]}}
                    g_ids.append(g.sub_sub_grp_id.id)
            self.sub_sub_grp_id = [(6,0,g_ids)]
        else:
            self.sub_sub_grp_id = [(6, 0, [])]

    @api.onchange('brand_id')
    def check_brand(self):
        check_brand_name = self.env['brand.main.custom'].search([('name', '=', self.brand_id.name)])


        if self.brand_id:
            self.default_code= check_brand_name.code

        else:
            self.default_code=''

    @api.constrains('default_code')
    def validate_part_num(self):
        for record in self:
            if record.default_code:
                check_record = self.env['product.product'].search([('default_code', '=', record.default_code), ('id', '!=', record.id)])
                if check_record:
                    raise ValidationError(
                        _('This Part Number has been already  registered'))




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



    # @api.depends('group_product_ids', 'group_product_ids.grp_id')
    # def set_domain_sub_grp(self):
    #
    #     # self.group_product_ids.grp_id = False
    #     for g in self.group_product_ids:
    #         if g.grp_id:
    #             return {'domain': {'sub_grp_id': [('grp_id', 'in', g.grp_id.id)]}}
    #
    #     else:
    #         # remove the domain if no grp is selected
    #         return {'domain': {'sub_grp_id': []}}
    #
    # @api.depends('group_product_ids', 'group_product_ids.sub_grp_id')
    # def set_domain_sub_sub_grp(self):
    #
    #     # self.group_product_ids.sub_grp_id = False
    #     for g in self.group_product_ids:
    #         # if self.group_product_ids:
    #         if g.sub_grp_id:
    #             return {'domain': {'sub_sub_grp_id': [('sub_grp_id', 'in', g.sub_grp_id.id)]}}
    #
    #     else:
    #         # remove the domain if no contrat is selected
    #         return {'domain': {'sub_sub_grp_id': []}}


class Brandsclass(models.Model):
    _name ='brand.custom'


    name = fields.Char('Name', required=True)
    code = fields.Char('Code')
    description = fields.Char('Description')










class SubGroupClass(models.Model):
    _name ='sub.group.custom'


    name = fields.Char('Name', required=True)
    code = fields.Char('Code')
    description = fields.Char('Description')
    grp_id = fields.Many2one('brand.custom',string="Group")





class SubSubGroupClass(models.Model):
    _name ='sub.sub.group.custom'


    name = fields.Char('Name',required=True)
    code = fields.Char('Code')
    description = fields.Char('Description')
    sub_grp_id = fields.Many2one('sub.group.custom',string="Sub Group")
    grp_id = fields.Many2one('brand.custom', string="Group")
    # brand_main_ids = fields.Many2one('brand.main.custom', string="Brand ID")




class BRandClass(models.Model):
    _name ='brand.main.custom'


    name = fields.Char('Name',required=True)
    code = fields.Char('Code')
    description = fields.Char('Description')



class ProductMaketype(models.Model):
    _name ='product.make.type'


    name = fields.Char('Name',required=True)
    code = fields.Char('Code')
    description = fields.Char('Description')



class PartsFamily(models.Model):
    _name ='parts.family'


    name = fields.Char('Name',required=True)
    code = fields.Char('Code')
    description = fields.Char('Description')
