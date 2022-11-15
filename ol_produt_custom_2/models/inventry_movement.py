from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import base64
import requests
import datetime
from odoo.exceptions import ValidationError


class InheritPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    order_type = fields.Selection(
        [('purchase_order', 'Purchase Order'), ('lpo', 'Lpo')],
        string='Purchase Order/Lpo',
        default='')


class InheritProductDashboard(models.TransientModel):
    _inherit = 'product.dashboard'

    purchase_two = fields.Many2many(comodel_name='purchase.order.line', compute="_get_lpo_history")

    lpo_order_ids = fields.Many2many(comodel_name='purchase.order.line',
                                     relation='contents_found',
                                     column1='lot_id',
                                     column2='content_id',
                                     string="Lpo History", compute="_get_lpo_history")

    @api.onchange('product_db_id', 'from_date', 'to_date', 'state')
    def _get_lpo_history(self):

        # raise UserError("hello ")

        all_warehouse = []

        if self.state:
            for a in self.state:
                # warehouseids = int(str(a.id)[6:])
                warehouseids = a._origin.id
                print(warehouseids)

                all_warehouse.append(warehouseids)

            # print(all_warehouse,'warehouse ids list')
            # raise UserError(str(all_warehouse))

        lpo = self.env['purchase.order.line'].search(
            [("product_id", "=", self.product_db_id.id),
             ('order_id.picking_type_id.warehouse_id.id', 'in', all_warehouse), '&',
             ('create_date', '>=', self.from_date),
             ('create_date', '<=', self.to_date)])
        # raise UserError(lpo)

        lpo_ids = []
        po_ids = []
        for line in lpo:
            if line.order_id.state == 'purchase' or line.order_id.state == 'done':
                if line.order_id.order_type == 'lpo':
                    lpo_ids.append(line.id)

                elif line.order_id.order_type == 'purchase_order':
                    po_ids.append(line.id)

            else:
                self.purchase_two = [(6, 0, po_ids)]

        self.lpo_order_ids = [(6, 0, lpo_ids)]
        self.purchase_two = [(6, 0, po_ids)]
        # print(warehouseids.view_location_id.name,'warehouse ids location')

        # warehouse = self.env['stock.warehouse'].search([('id', 'in', all_warehouse)])
        #
        # loc = warehouse.view_location_id
        # for l in loc.child_ids:
        #     print(l.complete_name)
        #     inventory = self.env['stock.quant'].search([('location_id', '=', l.id)])
        #     for ox in inventory:
        #         # print(ox.product_id.name, 'product')
        #         if self.product_db_id.id == ox.product_id.id:
        #             product=ox.product_id.id
        #             print(product, 'product')
        #
        #             print('yes matched the product name')
        #
        # for i in loc:
        #     print(i.id, 'location id')
        #     print(i.name, 'location')
        #     print(i.quant_ids.location_id.id, 'stock quant')
        #     print(i.product_id.name, 'product name')
        #     for o in i.quant_ids:
        #         print(o.id,'stock quant')
        #         print(o.product_id.name,'product name')

    quotation_two = fields.Many2many(comodel_name='sale.order.line',
                                     relation='contents_found',
                                     column1='lot_id',
                                     column2='content_id',
                                     string="Quotation", compute="_get_quotation_history_on_date_filter")
    customer_order_two = fields.Many2many(comodel_name='sale.order.line',
                                          relation='contents_found',
                                          column1='lot_id',
                                          column2='content_id',
                                          string="Sale", compute="_get_quotation_history_on_date_filter")

    @api.onchange('product_db_id', 'from_date', 'to_date', 'state')
    def _get_quotation_history_on_date_filter(self):

        all_warehousesale = []
        if self.state:
            for a in self.state:
                # warehouseids = int(str(a.id)[6:])
                warehouseids = a._origin.id
                # print(warehouseids)

                all_warehousesale.append(warehouseids)

            # print(all_warehousesale, 'warehouse ids list sale')
        sale_line_df = self.env['sale.order.line'].search(
            [("product_id", "=", self.product_db_id.id), ('order_id.warehouse_id.id', 'in', all_warehousesale), '&',
             ('create_date', '>=', self.from_date),
             ('create_date', '<=', self.to_date)])
        sadf_ids = []
        sodf_ids = []
        for line in sale_line_df:
            if line.order_id.state == 'draft':
                sadf_ids.append(line.id)
            elif line.order_id.state == 'sale':
                sodf_ids.append(line.id)
        self.quotation_two = [(6, 0, sadf_ids)]
        self.customer_order_two = [(6, 0, sodf_ids)]

    # internal_tranfer = fields.Many2many(comodel_name='stock.picking', compute="_get_received_order_on_date_filter")
    internal_tranfer = fields.Many2many(comodel_name='stock.move.line', compute="_get_received_order_on_date_filter")

    # received_id = fields.Many2many(comodel_name='stock.picking',

    received_id = fields.Many2many(comodel_name='stock.move.line',
                                   relation='contents_found',
                                   column1='lot_id',
                                   column2='content_id',
                                   string="Received", compute="_get_received_order_on_date_filter")
    # delivery_order_id = fields.Many2many(comodel_name='stock.picking',
    delivery_order_id = fields.Many2many(comodel_name='stock.move.line',
                                         relation='contents_found',
                                         column1='lot_id',
                                         column2='content_id',
                                         string="Delivery", compute="_get_received_order_on_date_filter")

    @api.onchange('product_db_id', 'from_date', 'to_date', 'state')
    def _get_received_order_on_date_filter(self):

        all_warehousetransfer = []
        if self.state:
            for a in self.state:
                # warehouseids = int(str(a.id)[6:])
                warehouseids = a._origin.id
                print(warehouseids)

                all_warehousetransfer.append(warehouseids)

            print(all_warehousetransfer, 'warehouse ids list transfer')
        stock_move = self.env['stock.move.line'].search(
            [("product_id", "=", self.product_db_id.id),
             ('picking_id.picking_type_id.warehouse_id.id', 'in', all_warehousetransfer), '&',
             ('create_date', '>=', self.from_date),
             ('create_date', '<=', self.to_date)])

        stock_picking = stock_move
        int_ids = []
        rec_ids = []
        dev_ids = []
        # sodf_ids = []
        for line in stock_picking:

            if line.picking_id.picking_type_id.name == 'Internal Transfers' and line.state == 'done':
                int_ids.append(line.id)

                # print(int_ids, 'list')
            elif line.picking_id.picking_type_id.name == 'Receipts' and line.state == 'done':
                rec_ids.append(line.id)

                # print(rec_ids, 'list')
            elif line.picking_id.picking_type_id.name == 'Delivery Orders' and line.state == 'done':
                dev_ids.append(line.id)

        self.internal_tranfer = [(6, 0, int_ids)]
        self.received_id = [(6, 0, rec_ids)]
        self.delivery_order_id = [(6, 0, dev_ids)]



    pos_db_ids = fields.Many2many(comodel_name='pos.order.line', compute="_get_posorder_history")

    @api.onchange('product_db_id')
    def _get_posorder_history(self):
        pos_orderline = self.env['pos.order.line'].search(
            [("product_id", "=", self.product_db_id.id)])
        print(pos_orderline.product_id.name, 'pos product')

        print(pos_orderline.order_id.picking_ids, 'pos delivery ')
        pos_list = []
        for pos in pos_orderline:
            if pos.order_id.state == 'done':
                pos_list.append(pos.id)
                print(pos_list, 'pos list')

        self.pos_db_ids = [(6, 0, pos_list)]

    pos_delivery = fields.Many2many(comodel_name='stock.move', compute="_get_posdel_history")

    @api.onchange('product_db_id')
    def _get_posdel_history(self):

        all_warehousetransfer = []
        if self.state:
            for a in self.state:
                # warehouseids = int(str(a.id)[6:])
                warehouseids = a._origin.id

                all_warehousetransfer.append(warehouseids)

        stock_move = self.env['stock.move'].search(
            [("product_id", "=", self.product_db_id.id),
             ('picking_id.picking_type_id.warehouse_id.id', 'in', all_warehousetransfer), '&',
             ('create_date', '>=', self.from_date),
             ('create_date', '<=', self.to_date)])

        posdel_list = []
        for line in stock_move:
            if line.picking_id.picking_type_id.name == 'PoS Orders':
                posdel_list.append(line.id)

        self.pos_delivery = [(6, 0, posdel_list)]

    pos_order_two = fields.Many2many(comodel_name='pos.order.line',
                                     relation='contents_found',
                                     column1='lot_id',
                                     column2='content_id',
                                     string="Received", compute="_get_posorder_ondate")

    @api.onchange('product_db_id', 'from_date', 'to_date', 'state')
    def _get_posorder_ondate(self):

        all_warehousesale = []
        if self.state:
            for a in self.state:
                # warehouseids = int(str(a.id)[6:])
                warehouseids = a._origin.id
                # print(warehouseids)

                all_warehousesale.append(warehouseids)

            # print(all_warehousesale, 'warehouse ids list sale')
        pos_ordertwo = self.env['pos.order.line'].search(
            [("product_id", "=", self.product_db_id.id),
             ('order_id.picking_type_id.warehouse_id.id', 'in', all_warehousesale), '&',
             ('create_date', '>=', self.from_date),
             ('create_date', '<=', self.to_date)])
        pos_two = []
        for pos in pos_ordertwo:
            if pos.order_id.state == 'done':
                pos_two.append(pos.id)
                print(pos_two, 'pos list')

        self.pos_order_two = [(6, 0, pos_two)]





    invoice_db_ids = fields.Many2many(comodel_name='account.move.line',
                                      relation='contents_found',
                                         column1='lot_id',
                                         column2='content_id',
                                         compute="_get_invoice_history", default=False)

    posinvoice_db_ids = fields.Many2many(comodel_name='account.move.line',
                                         relation='contents_found',
                                         column1='lot_id',
                                         column2='content_id',
                                         compute="_get_invoice_history", default=False)

    @api.depends('product_db_id')
    def _get_invoice_history(self):

        account_moveline = self.env['account.move.line'].search(
            [("product_id", "=", self.product_db_id.id)])
        print(account_moveline.product_id.name)
        # for l in  account_moveline.move_id :
        #     # print(l.move_type)

        invlist = []
        posinv_list = []
        if account_moveline:
            for inv in account_moveline:

                if inv.move_id.move_type == 'out_invoice':
                    vr = inv.move_id.payment_reference
                    # print(vr)
                    if vr[0] == 'I':
                        # print('TRUe')
                        invlist.append(inv.id)
                    else:
                        posinv_list.append(inv.id)

        self.invoice_db_ids = [(6, 0, invlist)]
        self.posinvoice_db_ids = [(6, 0, posinv_list)]