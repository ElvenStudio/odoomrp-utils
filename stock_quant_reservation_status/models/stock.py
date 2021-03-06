# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api, _


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    is_reserved = fields.Boolean(
        string=_('Reserved Quant'),
        compute='_is_reserved',
        store=True
    )

    reserved_for = fields.Char(
        string=_('Reserved for'),
        compute='_reserved_for'
    )

    @api.one
    @api.depends('reservation_id')
    def _reserved_for(self):
        reserved_for = ''
        if self.reservation_id:
            partner_name = self.reservation_id.picking_id.partner_id.name or ''
            picking_name = self.reservation_id.picking_id.name or ''

            if self.reservation_id.picking_id.sale_id:
                origin = self.reservation_id.picking_id.sale_id.name or ''
            else:
                origin = self.reservation_id.picking_id.origin or ''

            reserved_for = origin + '\n' + picking_name + '\n' + partner_name

        self.reserved_for = reserved_for

    @api.one
    @api.depends('reservation_id')
    def _is_reserved(self):
        self.is_reserved = bool(self.reservation_id)

    @api.multi
    def action_view_related_picking(self):
        pickings = self.mapped('reservation_id').mapped('picking_id')
        ir_model_data = self.env['ir.model.data']
        act_window = self.env['ir.actions.act_window']

        picking_model_name = 'stock'
        picking_form_view_name = 'view_picking_form'
        picking_action_name = 'action_picking_tree_all'

        result = ir_model_data.get_object_reference(picking_model_name, picking_action_name)
        view_id = result and result[1] or False
        result = act_window.browse(view_id).read()[0]

        if len(pickings) > 1:
            result['domain'] = "[('id','in'," + str(pickings.ids) + ")]"
        else:
            res = ir_model_data.get_object_reference(picking_model_name, picking_form_view_name)
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = pickings and pickings.ids[0] or False

        return result

    @api.multi
    def action_view_related_sale_order(self):
        orders = self.mapped('reservation_id').mapped('picking_id').mapped('sale_id')
        ir_model_data = self.env['ir.model.data']
        act_window = self.env['ir.actions.act_window']

        sale_model_name = 'sale'
        sale_form_view_name = 'view_order_form'
        sale_action_name = 'action_orders'

        result = ir_model_data.get_object_reference(sale_model_name, sale_action_name)
        view_id = result and result[1] or False
        result = act_window.browse(view_id).read()[0]

        if len(orders) > 1:
            result['domain'] = "[('id','in'," + str(orders.ids) + ")]"
        else:
            res = ir_model_data.get_object_reference(sale_model_name, sale_form_view_name)
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = orders and orders.ids[0] or False

        return result
