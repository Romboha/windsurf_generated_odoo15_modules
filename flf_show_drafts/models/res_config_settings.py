# -*- coding: utf-8 -*-

from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    show_drafts_in_overview = fields.Boolean(
        string="Show Drafts in Inventory Overview",
        related='company_id.show_drafts_in_overview_setting',
        readonly=False,
        help="Enable this to display the count of draft pickings in the Inventory Overview for the selected company."
    )
