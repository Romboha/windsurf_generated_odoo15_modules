# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval # Додано імпорт
import logging

_logger = logging.getLogger(__name__)

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    draft_count = fields.Integer(
        string='Draft Count',
        compute='_compute_draft_count',
        store=True
    )
    
    show_drafts_enabled = fields.Boolean(
        string='Show Drafts Enabled',
        compute='_compute_show_drafts_enabled',
        store=True
    )

    @api.depends('company_id.show_drafts_in_overview_setting') # Залежність від налаштування компанії
    def _compute_show_drafts_enabled(self):
        _logger.info(f"FLF_SHOW_DRAFTS: Computing show_drafts_enabled for {len(self)} types")
        for picking_type in self:
            enabled = False
            if picking_type.company_id:
                enabled = picking_type.company_id.show_drafts_in_overview_setting
                _logger.info(f"FLF_SHOW_DRAFTS: show_drafts_enabled for {picking_type.name} (ID: {picking_type.id}, Company: {picking_type.company_id.name}): {enabled}")
            else:
                _logger.info(f"FLF_SHOW_DRAFTS: No company for {picking_type.name} (ID: {picking_type.id}). Setting show_drafts_enabled to False")
            picking_type.show_drafts_enabled = enabled

    @api.depends('show_drafts_enabled') # Залежність від show_drafts_enabled
    def _compute_draft_count(self):
        _logger.info(f"FLF_SHOW_DRAFTS: Starting _compute_draft_count for {len(self)} types: {[pt.name for pt in self]}")
        
        # Фільтруємо типи операцій, для яких потрібно обчислювати лічильник
        types_to_compute = self.filtered(lambda pt: pt.show_drafts_enabled and pt.company_id)
        
        if not types_to_compute:
            for picking_type in self:
                picking_type.draft_count = 0
            return

        # Використовуємо read_group для ефективного підрахунку
        pickings_data = self.env['stock.picking'].read_group(
            [
                ('picking_type_id', 'in', types_to_compute.ids),
                ('state', '=', 'draft'),
                ('company_id', 'in', types_to_compute.mapped('company_id').ids) # Рахуємо для відповідних компаній
            ],
            ['picking_type_id'],
            ['picking_type_id']
        )
        
        counts_map = {data['picking_type_id'][0]: data['picking_type_id_count'] for data in pickings_data}

        for picking_type in self:
            if picking_type in types_to_compute:
                picking_type.draft_count = counts_map.get(picking_type.id, 0)
                _logger.info(f"FLF_SHOW_DRAFTS: Computed draft_count {picking_type.draft_count} for {picking_type.name} (ID: {picking_type.id}, Company: {picking_type.company_id.name})")
            else:
                # Для типів, де show_drafts_enabled = False, або немає компанії
                picking_type.draft_count = 0
                if not picking_type.company_id:
                     _logger.warning(f"FLF_SHOW_DRAFTS: Picking type {picking_type.name} (ID: {picking_type.id}) has no company_id. Setting draft_count to 0.")
                _logger.info(f"FLF_SHOW_DRAFTS: Draft count for {picking_type.name} (ID: {picking_type.id}) set to 0 as show_drafts_enabled is False or no company.")


    def get_picking_type_draft_action(self):
        action = self.env.ref('stock.stock_picking_action_picking_type').read()[0]
        action['name'] = _('Draft Pickings')
        action['display_name'] = _('Draft Pickings')
        
        ctx_str = action.get('context', '{}') 
        ctx_dict = {}
        if isinstance(ctx_str, str):
            try:
                ctx_dict = safe_eval(ctx_str)
            except Exception as e:
                _logger.error(f"FLF_SHOW_DRAFTS: Error evaluating context string: {ctx_str}. Error: {e}")
                ctx_dict = {} 
        elif isinstance(ctx_str, dict): 
             ctx_dict = dict(ctx_str) 

        # Додаємо фільтри за замовчуванням до контексту
        # 'search_default_draft': 1 активує стандартний фільтр <filter name="draft" .../>
        # 'search_default_picking_type_id': self.id активує фільтр за поточним типом операції
        ctx_dict.update({
            'search_default_draft': 1, 
            'search_default_picking_type_id': self.id,
        })
        action['context'] = ctx_dict

        # Додаємо явний домен для picking_type_id, щоб він залишався,
        # навіть якщо користувач видалить фільтр picking_type_id з панелі пошуку.
        # Стандартний фільтр 'draft' вже подбає про ('state', '=', 'draft').
        existing_domain = action.get('domain', [])
        if isinstance(existing_domain, str): 
            try:
                existing_domain = safe_eval(existing_domain)
                if not isinstance(existing_domain, list): # Переконуємося, що це список
                    existing_domain = []
            except Exception:
                existing_domain = [] 
        
        # Об'єднуємо існуючий домен з нашим фільтром picking_type_id
        # ['&'] + domain1 + domain2
        if existing_domain:
            # Якщо existing_domain вже містить ('picking_type_id', '=', self.id), не додаємо його знову
            is_picking_type_present = any(
                isinstance(term, (list, tuple)) and len(term) == 3 and 
                term[0] == 'picking_type_id' and term[1] == '=' and term[2] == self.id 
                for term in existing_domain
            )
            if not is_picking_type_present:
                action['domain'] = ['&'] + existing_domain + [('picking_type_id', '=', self.id)]
            else:
                action['domain'] = existing_domain # Вже містить, нічого не змінюємо
        else:
            action['domain'] = [('picking_type_id', '=', self.id)]
        
        _logger.info(f"FLF_SHOW_DRAFTS: Action for draft pickings: {action}")
        return action
