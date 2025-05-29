# -*- coding: utf-8 -*-

from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _trigger_draft_count_recompute(self):
        """ Triggers recomputation of draft_count for related picking types. """
        picking_type_ids = self.mapped('picking_type_id').ids
        if picking_type_ids:
            _logger.info(f"FLF_SHOW_DRAFTS: Triggering draft_count recompute for picking types: {picking_type_ids} due to changes in pickings: {self.ids}")
            self.env['stock.picking.type'].browse(picking_type_ids)._compute_draft_count()

    @api.model_create_multi
    def create(self, vals_list):
        pickings = super(StockPicking, self).create(vals_list)
        pickings._trigger_draft_count_recompute()
        return pickings

    def write(self, vals):
        res = super(StockPicking, self).write(vals)
        if 'state' in vals or 'picking_type_id' in vals:
            self._trigger_draft_count_recompute()
        return res

    def unlink(self):
        # Store picking_type_ids before unlinking, as they won't be accessible afterwards
        picking_type_ids_to_update = self.mapped('picking_type_id').ids
        res = super(StockPicking, self).unlink()
        if picking_type_ids_to_update:
            _logger.info(f"FLF_SHOW_DRAFTS: Triggering draft_count recompute for picking types: {picking_type_ids_to_update} due to unlinking pickings.")
            self.env['stock.picking.type'].browse(picking_type_ids_to_update)._compute_draft_count()
        return res
