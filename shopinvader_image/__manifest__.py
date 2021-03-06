# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Shopinvader image",
    "summary": "Add the export of Image for Shopinvader",
    "version": "10.0.1.0.1",
    "category": "e-commerce",
    "website": "https://akretion.com",
    "author": "Akretion",
    "license": "AGPL-3",
    "depends": ["shopinvader", "storage_image_product"],
    "data": [
        "security/ir.model.access.csv",
        "views/shopinvader_backend_view.xml",
        "views/shopinvader_image_resize_view.xml",
        "data/ir_export_product.xml",
        "data/ir_export_category.xml",
    ],
    "demo": [
        "demo/shopinvader_image_resize_demo.xml",
        "demo/backend_demo.xml",
    ],
    "post_init_hook": "post_init_hook",
}
