# -*- coding: utf-8 -*-
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def _recompute_all_draft_counts(cr, registry):
    """ 
    This hook is called after the module installation or update.
    It recomputes the 'draft_count' for all stock.picking.type records.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    picking_types = env['stock.picking.type'].search([])
    if not picking_types:
        _logger.info("FLF_SHOW_DRAFTS: Post-init hook: No picking types found to recompute draft_count.")
        return

    _logger.info(f"FLF_SHOW_DRAFTS: Post-init hook: Recomputing draft_count for {len(picking_types)} picking types.")
    
    # Виклик обчислювального методу. Це змусить значення оновитися в базі даних,
    # оскільки поле має store=True.
    picking_types._compute_draft_count()
    
    # Можна додати flush(), щоб переконатися, що зміни записані, хоча це зазвичай
    # відбувається автоматично в кінці транзакції.
    # env.cr.commit() # Не робіть commit всередині хука, Odoo зробить це.

    _logger.info("FLF_SHOW_DRAFTS: Post-init hook: Finished recomputing draft_count.")

