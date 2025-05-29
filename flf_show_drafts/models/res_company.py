# -*- coding: utf-8 -*-

from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    show_drafts_in_overview_setting = fields.Boolean(
        string="Show Drafts in Inventory Overview",
        default=False,
        help="If checked, the count of draft pickings will be shown in the Inventory Overview for this company."
    )
    
    def write(self, vals):
        """Override write to trigger recomputation of show_drafts_enabled in stock.picking.type
        when show_drafts_in_overview_setting changes."""
        result = super(ResCompany, self).write(vals)
        
        # If show_drafts_in_overview_setting was changed
        if 'show_drafts_in_overview_setting' in vals:
            # Find all picking types related to these companies
            picking_types = self.env['stock.picking.type'].search([('company_id', 'in', self.ids)])
            if picking_types:
                # Force recomputation of show_drafts_enabled
                picking_types._compute_show_drafts_enabled()
                
        return result
