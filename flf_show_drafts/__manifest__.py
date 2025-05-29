# -*- coding: utf-8 -*-
{
    'name': 'Show Draft Pickings on Overview',
    'version': '15.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Adds a counter for draft pickings to the inventory overview.',
    'description': """
Цей модуль додає лічильник чернеток документів переміщення на картки типів операцій в огляді складу. Видимість лічильника контролюється налаштуванням для кожної компанії, а клік по ньому відкриває відфільтрований список відповідних чернеток.
    """,
    'author': 'FLF',
    'website': '',
    'depends': ['stock'],
    'data': [
        'views/stock_picking_type_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': '_recompute_all_draft_counts',
    'license': 'LGPL-3',
}
