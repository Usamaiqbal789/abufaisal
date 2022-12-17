from odoo import models, fields,api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import base64
import requests
import datetime
from odoo.exceptions import ValidationError


class image(models.Model):
    _inherit = 'product.template'

    attachment_ids = fields.Many2many('ir.attachment',
                                      string='Files')





class AccountmoveINherit(models.Model):
    _inherit = 'product.product'

    # product_i = fields.Many2one(related="product_variant_id.alternative_product_ids", string='Reference')
    alternative_product_ids = fields.One2many('alternative.product.line','alternative_product_id')
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

    # own_ref_no = fields.Integer('Own Reference Number',compute='check_own_ref_no_dup',store=True)
    own_ref_no = fields.Char(string='Own Reference', required=False, copy=False, index=True, )
    origin = fields.Many2one('res.country',string='Origin')

    part_num = fields.Char('Part Number')
    part_name = fields.Char('Part Name')
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
    product_notes_ids = fields.One2many('product.notes.line','notes_id')
    trader = fields.Float('Trader')
    export_price = fields.Float('Export Price')
    specification = fields.Char('Specification')
    @api.model
    def create(self, vals):
        # print(vals.get('name_seq'))
        if vals.get('own_ref_no', _('New')) == _('New'):
            vals['own_ref_no'] = self.env['ir.sequence'].next_by_code('product.product') or _('New')
        result = super(AccountmoveINherit, self).create(vals)
        return result

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
                    g_ids.append(g.sub_sub_grp_id.id)
            self.sub_sub_grp_id = [(6,0,g_ids)]
        else:
            self.sub_sub_grp_id = [(6, 0, [])]

    @api.onchange('brand_id')
    def check_brand(self):
        check_brand_name = self.env['brand.main.custom'].search([('name', '=', self.brand_id.name)])


        if self.brand_id:
            self.default_code = check_brand_name.code

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


    pricelist_ids= fields.One2many('product.pricelist.item','product_id',string="Price List")


    alternate_product_warning=fields.Char("Warning")
    alternate_product_warning_show=fields.Char("Warning_show",default=False)
    @api.onchange('alternative_products','alternative_products.default_code')
    def check_alternat_product(self):
        # var = self.env['product.product'].search(['id','=',self.alternative_products.ids])
        # raise ValidationError(var)
        all_product = self.alternative_products.ids

        self.alternate_product_warning_show = False
        self.alternate_product_warning = ""

        thisid=0
        try:
            thisid=int(self.id)
        except :
            # raise ValidationError(self.id)
            try:
                thisid=int(str(self.id)[6:])
            except:
                self.alternate_product_warning_show=True
                self.alternate_product_warning="You cannot add alternate products without saving this product. Please save this product first and then try again."
                self.write({"alternative_products": [(6, 0, [])]})
                return
        all_product.append(thisid)


        altproducts = self.env['product.product'].search([('id', 'in', all_product)])
        for altproduct in altproducts:
            for id in altproduct.alternative_products.ids:
                if id not in all_product:
                    all_product.append(id)

        altproducts = self.env['product.product'].search([('id', 'in', all_product)])

        for altproduct in altproducts:
            appendableProducts=[i for i in all_product if i!=altproduct.id]
            altproduct.write({"alternative_products":[(6, 0, appendableProducts)]})



        appendableProducts = [i for i in all_product if i != self.ids[0]]
        self.write({"alternative_products": [(6, 0, appendableProducts)]})


    # @api.onchange('product_db_id')
    # def send_comment(self):
    #     print('hello comment')
    #     comments_line = self.env['product.dashboard'].search([('product_db_id', '=', self.id)])
    #     # for i in comments_line:
    #     print(comments_line.id, 'notes')
    #     print(comments_line.curr_user, 'current user')
    #     if comments_line.product_dashboard_notes_ids:
    #         for lines in comments_line.product_dashboard_notes_ids:
    #             vlas = {
    #                 'current_user': lines.curr_user,
    #                 'current_date': lines.curr_date,
    #                 'des': lines.des,
    #
    #             }
    #             notes = self.env['product.notes.line'].write(vlas)
    #             print(notes)

        # for i in

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





class AlternativeProduct(models.Model):
    _name = 'alternative.product.line'

    alternative_product_id = fields.Many2one('product.product', string='Alternate Product')
    product_id = fields.Many2one('product.product', string='Product Name')
    price_unit = fields.Float(string='Unit Price', default=1)


class InheritSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    partner_id = fields.Many2one('res.partner',related="order_id.partner_id", string='Customer')

    # @api.onchange("product_id")
    # def product_id_change(self):
    #     res = super(InheritSaleOrderLine, self).product_id_change()
    #     for i in self:
    #         if i.product_id:
    #             product = self.env['product.product'].search([("id", "=", self.product_id.id)])
    #             # print(product)
    #             i.name = product.parts_family_id.name
    #             # print(self.name)
    #
    #         else:
    #             self.name = ''
    #
    #     return res






class ProductNotes(models.Model):
    _name = 'product.notes.line'

    current_user = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.user)
    current_date = fields.Datetime(default=fields.datetime.now(), store=True, string="Date")
    des = fields.Char(string="Description")
    notes_id = fields.Many2one('product.product')

class Inheritstockwarehouse(models.Model):
    _inherit = 'stock.warehouse'

    ware_type = fields.Selection([('shop', 'Shop'), ('warehouse', 'Ware House')])

class Inheritstocklocation(models.Model):
    _inherit = 'stock.location'

    type = fields.Char('Type')
    cus_warehouse_id = fields.Many2one('stock.warehouse')
    # type = fields.Selection([],related="cus_warehouse_id.ware_type")
    type = fields.Char('Type')




    @api.onchange('location_id')
    def _get_type_from_stockwarehouse(self):
        print('ware location')
        self.cus_warehouse_id = self.location_id.id
        print(self.cus_warehouse_id.id,'stock.warehouse')
        # warehouse = self.env['stock.warehouse'].search([("name", "=", self.cus_warehouse_id.name)])
        warehouse = self.env['stock.warehouse'].search([("id", "=", 1)])
        print(warehouse.name,'warehouse type')

    # type = fields.Selection('Type', related="cus_warehouse_id.ware_type")






