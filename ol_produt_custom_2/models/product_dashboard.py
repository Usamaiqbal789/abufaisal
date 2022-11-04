from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import base64
import requests
import datetime
from odoo.exceptions import ValidationError


class CustomDashboard(models.TransientModel):
    _name = 'product.dashboard'
    _rec_name = 'product_db_id'

    curr_user_1 = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.user)
    shop_ids = fields.Many2many('dashboard.shop')

    product_db_id = fields.Many2one('product.product', string="Part Number")
    # sale_his_id = fields.Many2many('sale.order.line', string="Sale History")
    quotation_his_id = fields.Many2many(comodel_name='sale.order',
                                        relation='contents_found',
                                        column1='lot_id',
                                        column2='content_id',
                                        string="Quotation History")
    customer_order_ids = fields.Many2many(comodel_name='sale.order',
                                          relation='contents_found',
                                          column1='lot_id',
                                          column2='content_id',
                                          string="Order History")

    sale_his_id = fields.Many2many(comodel_name='sale.order.line', string="Sale History")
    # relation='contents_found',
    # column1='lot_id',
    # column2='content_id',string="Sale History")

    purchase_his_id = fields.Many2many('purchase.order.line', string="Purchase History")
    account_his_id = fields.Many2many('account.move', string="Invoice")
    # inventory_his_id = fields.Many2many('purchase.order', string="purchase")
    product_code = fields.Char(string="Product Code")
    des = fields.Char(string="Description")
    own_ref_no = fields.Char(string="Own Ref No", related='product_db_id.own_ref_no')
    spec = fields.Char(string="Specification")
    product_brand = fields.Many2one(string="Product Brand", related='product_db_id.brand_id')
    packet_detials = fields.Char(string="Packet Details")
    eta = fields.Char(string="ETA")
    etd = fields.Char(string="ETD")
    oem = fields.Char(string="OEM Code", related='product_db_id.oem_code')
    parts_fam = fields.Many2one(string="Parts Family", related='product_db_id.categ_id', readonly=True)
    # delivery_order_his = fields.Many2many('stock.picking', string="Delivery History")
    delivery_order_his = fields.Many2many('dashboard.delivery', string="Delivery History")
    substitute_product = fields.Many2many('product.product', string="Substitute Product")
    part_no = fields.Char(string="Part No", related='product_db_id.default_code')
    part_name = fields.Char(string="Part Name",related='product_db_id.name')
    product_dashboard_notes_ids = fields.One2many('product.notes.dashboard.line', 'pro_dash')
    warehouse_ids = fields.Many2many('stock.quant')
    product_groups_ids = fields.Many2many('groups.product')
    reorder_quan_ids = fields.Many2many('stock.warehouse.orderpoint')
    product_image = fields.Binary('Image')

    # re_order_level = fields.Char(string="Re Order Level")
    # re_order_qty = fields.Char(string="Re Order Qty")
    # unit = fields.Char(string="unit")
    # supp_refno = fields.Char(string="Supplier Ref. No")
    # last_supp = fields.Char(string="Last Supplier")
    # last_pur_cost = fields.Char(string="Last Purchase Cost")
    # avg_cost = fields.Char(string="Avg  Cost")
    # location = fields.Char(string="Location")
    # Stock_type = fields.Char(string="Stock Type")
    # min_unit_price = fields.Char(string="Min Unit Price")
    # unit_price = fields.Char(string="Min Unit Price")
    # margin = fields.Char(string="Margin %")
    # vat_out = fields.Char(string="Vat Out")
    # price_vat = fields.Char(string="Price With Vat")
    # dail_tracs_item = fields.Boolean(string="Daily Transaction item")
    # origin_p = fields.Char(string="Origin")
    # remark = fields.Char(string="Remark")

    # qty_on_hand = fields.Char(string="Qty ON Hand")
    # product_type_p = fields.Char(string="Product Type")
    # # multi_loc = fields.Many2many('stock.quant',string="Multiple Location")
    # parts_type = fields.Char(string="Parts Type")

    # Chase_no = fields.Char(string="Chase No")
    # model = fields.Char(string="Model")
    # engine_no = fields.Char(string="Engine No")

    # image
    @api.onchange('product_db_id')
    def _get_product_image(self):
        img = self.env['product.product'].search([("id", "=", self.product_db_id.id)])
        if self.product_db_id:
            self.product_image = img.image_1920
        else:
            self.product_image = ''

    # quotation history
    @api.onchange('product_db_id')
    def _get_quotation_history(self):
        sale_line_q = self.env['sale.order.line'].search([("product_id", "=", self.product_db_id.id)])
        quotation = sale_line_q.order_id
        sa_ids = []
        for line in quotation:
            if line.state == 'draft':

                sa_ids.append(line.id)

                self.quotation_his_id = sa_ids


            else:
                pass

    # customer order

    @api.onchange('product_db_id')
    def _get_customerOrder_history(self):
        sale_done = ''
        # self.customer_order_ids= False
        # print('hello purchase')
        sale_line = self.env['sale.order.line'].search([("product_id", "=", self.product_db_id.id)])
        sale_order = sale_line.order_id
        sa_ids = []
        for line in sale_order:
            if line.state == 'sale':

                sa_ids.append(line.id)

                self.customer_order_ids = sa_ids


            else:
                pass

    # sale history
    @api.onchange('product_db_id')
    def _get_sale_history(self):

        sale_lines = self.env['sale.order.line'].search([("product_id", "=", self.product_db_id.id)])

        g_ids = []
        if sale_lines:

            for lines in sale_lines:
                if self.product_db_id:
                    g_ids.append(lines.id)

            self.sale_his_id = [(6, 0, g_ids)]
        else:
            self.sale_his_id = [(6, 0, [])]

    # substitute products

    @api.onchange('product_db_id')
    def _get_substitute_product(self):
        subs = self.env['product.product'].search([("id", "=", self.product_db_id.id)])
        p_ids = []
        if self.product_db_id:
            for lines in subs.alternative_products:
                # if self.product_db_id:
                p_ids.append(lines.id)

            self.substitute_product = [(6, 0, p_ids)]
        else:
            self.substitute_product = [(6, 0, [])]

    # product groups
    @api.onchange('product_db_id')
    def _get_groups_product(self):
        groups = self.env['product.product'].search([("id", "=", self.product_db_id.id)])
        p_ids = []
        if self.product_db_id:
            for lines in groups.group_product_ids:
                p_ids.append(lines.id)

            self.product_groups_ids = [(6, 0, p_ids)]
        else:
            self.product_groups_ids = [(6, 0, [])]

    # reorder
    @api.onchange('product_db_id')
    def _get_reorder_history(self):

        record = self.env['product.product'].search([("id", "=", self.product_db_id.id)])
        # print(record.id)
        reorder = record.orderpoint_ids
        print(reorder.ids, 'reorder id')

        re_ids = []
        if reorder:

            for lines in reorder:
                re_ids.append(lines.id)
                print(re_ids)

                self.reorder_quan_ids = [(6, 0, re_ids)]
        else:
            self.reorder_quan_ids = [(6, 0, [])]




    @api.onchange('product_db_id')
    def _get_customerDelivery_history(self):
        # print('inside the dilevery function')
        Transfer_lines = self.env['stock.picking'].search(
            [("product_id", "=", self.product_db_id.id)])

        del_list = []
        if Transfer_lines:

            for st in Transfer_lines:

                for i in st.move_ids_without_package:
                    dev_lines = self.env['dashboard.delivery'].create({
                        "ref": st.name,
                        "customer": st.partner_id.name,
                        "shud_date": st.scheduled_date,
                        "demand": i.product_uom_qty,
                        "done": i.quantity_done,

                    })

                del_list.append(dev_lines.id)

                self.write({
                    'delivery_order_his': [(6, 0, del_list)]

                })

        else:
            pass

    @api.onchange('product_db_id')
    def _get_shop_history(self):
        pro = self.env['product.product'].search(
            [("id", "=", self.product_db_id.id)])

        # raise ValidationError(Transfer_lines)
        pro_list = []

        if pro:

            # for p in pro:

            rec = self.env['stock.warehouse'].search([])  # location page

            for i in rec:
                if i.ware_type:
                    print(i.name)
                    print(i.ware_type)

            # loc = None
            for o in rec:
                # for w in p.warehouse_id:
                shop_lines = self.env['dashboard.shop'].create({
                    # "branch": o.location_id.location_id.name,
                    "cost": pro.standard_price,
                    "min_price": pro.min_unit_price,
                    "max_price": pro.lst_price,
                    "trader": pro.trader,
                    "export_price": pro.export_price,

                })

                pro_list.append(shop_lines.id)

                self.write({
                    'shop_ids': [(6, 0, pro_list)]

                })

        else:
            pass

    @api.onchange('product_dashboard_notes_ids')
    def send_comment(self):
        print('hello comment')
        prod = self.env['product.product'].search([("id", "=", self.product_db_id.id)])
        print(prod.name)
        notes_list = []
        if self.product_dashboard_notes_ids:
            for lines in self.product_dashboard_notes_ids:
                print(lines.curr_user.name)
                print(lines.curr_date)
                print(lines.des)
                noteobj = self.env['product.notes.line'].create({
                        "current_user": lines.curr_user.id,
                        "current_date": lines.curr_date,
                        "des": lines.des,

                })
                notes_list.append(noteobj.id)
                # print(notes_list)
            # prod.product_notes_ids = [(6, 0, notes_list)]

                # prod.write({
                #         'product_notes_ids': [(6, 0, notes_list)]
                #
                #     })

                # n_lines = self.env['product.notes.line'].write({
                #     "current_user": lines.curr_user,
                #     "current_date": lines.curr_date,
                #     "des": lines.des,
                #
                #
                # })
                # notes_list.append(n_lines.id)
                #
            prod.write({
                 'product_notes_ids': [(6, 0, notes_list)]

            })
            # print(prod.product_notes_ids.current_user)
            # print(prod.product_notes_ids.current_date)
            # print(prod.product_notes_ids.des)

        else:
            pass

    @api.onchange('product_db_id')
    def _get_part_no_only(self):
        print("split")
        if self.product_db_id:
            a = self.product_db_id.default_code
            # c= a)
            print(a)
            x = a.split(']')
            b = x[0].split('[')

            print(b,'product')
        







class ProductNotesDash(models.TransientModel):
    _name = 'product.notes.dashboard.line'

    curr_user = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.user)
    curr_date = fields.Datetime(default=fields.datetime.now(), store=True, string="Date")
    des = fields.Char(string="Comments")
    pro_dash = fields.Many2one('product.dashboard')


class Dashboarddelivery(models.TransientModel):
    _name = 'dashboard.delivery'

    ref = fields.Char('reference')
    customer = fields.Char('Customer')
    shud_date = fields.Datetime(default=fields.datetime.now(), store=True, string="Date")
    demand = fields.Float("Demand")
    done = fields.Float("Done")


class Dashboardshopcustom(models.Model):
    _name = 'dashboard.shop'

    branch = fields.Char('Branch')
    cost = fields.Char('Cost')
    min_price = fields.Char(string="Min Price")
    max_price = fields.Char(string="Max price")
    trader = fields.Char(string="Trader")
    export_price = fields.Char(string="Export Price")


class Dashboardcustomwarehouse(models.Model):
    _name = 'dashboard.warehouse'

    branch = fields.Char('Branch')
    # cost = fields.Char('Cost')
    # min_price = fields.Char(string="Min Price")
    # max_price = fields.Char(string="Max price")
    # trader = fields.Char(string="Trader")
    # export_price = fields.Char(string="Export Price")

