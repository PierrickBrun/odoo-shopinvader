# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import ProductCommonCase


class ProductCase(ProductCommonCase):

    def install_lang(self, lang_xml_id):
        lang = self.env.ref(lang_xml_id)
        wizard = self.env['base.language.install'].create({
            'lang': lang.code,
            })
        wizard.lang_install()
        return lang

    def test_create_shopinvader_variant(self):
        self.assertEqual(
            len(self.template.product_variant_ids),
            len(self.shopinvader_variants))

# TODO MIGRATE
#    def test_categories(self):
#        self.assertEqual(
#            len(self.shopinvader_variant.shopinvader_categ_ids), 0)
#        self.backend.bind_all_category()
#        self.shopinvader_variant.invalidate_cache()
#        self.assertEqual(
#            len(self.shopinvader_variant.shopinvader_categ_ids), 2)
#        self.assertEqual(
#            self.shopinvader_variant.shopinvader_categ_ids.mapped('record_id'),
#            self.template.categ_id + self.template.categ_id.parent_id)
#
    def test_variant_attributes(self):
        attr_dict = {'color': u'Black',
                     'wi-fi': u'2.4 GHz',
                     'memory': u'16 GB'}
        self.assertDictEqual(
            self.shopinvader_variant.variant_attributes, attr_dict)

    def test_product_filter(self):
        field_id = self.env['ir.model.fields'].search([
            ('model', '=', 'shopinvader.product'),
            ('name', '=', 'name')])
        filter_on_field = self.env['product.filter'].create(
            {'name': 'Test Filter on field name',
             'based_on': 'field',
             'field_id': field_id.id})
        self.assertEqual(filter_on_field.display_name, 'name')

        attribute_id = self.env['product.attribute'].search([
            ('name', '=', 'Wi-Fi')])
        filter_on_attr = self.env['product.filter'].create(
            {'name': 'Test Filter on field name',
             'based_on': 'variant_attribute',
             'variant_attribute_id': attribute_id.id})
        self.assertEqual(
            filter_on_attr.display_name, 'variant_attributes.wi-fi')

    def test_product_price(self):
        self.assertEqual(
            self.shopinvader_variant.price,
            {'default': {
                'discount': 0.0,
                'original_value': 750.0,
                'tax_included': True,
                'value': 750.0,
                }}
            )

    def test_product_get_price(self):
        # base_price_list doesn't define a tax mapping. We are tax included
        base_price_list = self.env.ref('product.list0')
        fiscal_position_fr = self.env.ref('shopinvader.fiscal_position_0')
        price = self.shopinvader_variant._get_price(
            base_price_list, fiscal_position_fr)
        self.assertDictEqual(
            price,
            {
                'discount': 0.0,
                'original_value': 750.0,
                'tax_included': True,
                'value': 750.0,
            }
        )
        # promotion price list define a discount of 20% on all product
        promotion_price_list = self.env.ref("shopinvader.pricelist_1")
        price = self.shopinvader_variant._get_price(
            promotion_price_list, fiscal_position_fr)
        self.assertDictEqual(
            price,
            {
                'discount': 0.0,
                'original_value': 600.0,
                'tax_included': True,
                'value': 600.0,
            }
        )
        # use a fiscal position defining a mapping from tax included to tax
        # excluded
        tax_exclude_fiscal_position = self.env.ref(
            "shopinvader.fiscal_position_1")
        price = self.shopinvader_variant._get_price(
            base_price_list, tax_exclude_fiscal_position)
        self.assertDictEqual(
            price,
            {
                'discount': 0.0,
                'original_value': 652.17,
                'tax_included': False,
                'value': 652.17,
            }
        )
        price = self.shopinvader_variant._get_price(
            promotion_price_list, tax_exclude_fiscal_position)
        self.assertDictEqual(
            price,
            {
                'discount': 0.0,
                'original_value': 521.74,
                'tax_included': False,
                'value': 521.74,
            }
        )

    def test_product_get_price_discount_policy(self):
        # Ensure that discount is with 2 digits
        self.env.ref('product.decimal_discount').digits = 2
        # base_price_list doesn't define a tax mapping. We are tax included
        # we modify the discount_policy
        base_price_list = self.env.ref('product.list0')
        base_price_list.discount_policy = 'without_discount'
        fiscal_position_fr = self.env.ref('shopinvader.fiscal_position_0')
        price = self.shopinvader_variant._get_price(
            base_price_list, fiscal_position_fr)
        self.assertDictEqual(
            price,
            {'tax_included': True,
             'value': 750.0,
             'discount': 0.0,
             'original_value': 750.0}
        )
        # promotion price list define a discount of 20% on all product
        # we modify the discount_policy
        promotion_price_list = self.env.ref("shopinvader.pricelist_1")
        promotion_price_list.discount_policy = 'without_discount'
        price = self.shopinvader_variant._get_price(
            promotion_price_list, fiscal_position_fr)
        self.assertDictEqual(
            price,
            {'tax_included': True,
             'value': 600.0,
             'discount': 20.0,
             'original_value': 750.0}
        )
        # use the fiscal position defining a mapping from tax included to tax
        # excluded
        # Tax mapping should not impact the computation of the discount and
        # the original value
        tax_exclude_fiscal_position = self.env.ref(
            "shopinvader.fiscal_position_1")
        price = self.shopinvader_variant._get_price(
            base_price_list, tax_exclude_fiscal_position)
        self.assertDictEqual(
            price,
            {'tax_included': False,
             'value': 652.17,
             'discount': 0.0,
             'original_value': 652.17}
        )
        price = self.shopinvader_variant._get_price(
            promotion_price_list, tax_exclude_fiscal_position)
        self.assertDictEqual(
            price,
            {'tax_included': False,
             'value': 521.74,
             'discount': 20.0,
             'original_value': 652.17,
             }
        )

    def test_category_child_with_one_lang(self):
        self.backend.bind_all_category()
        categ = self.env.ref('product.product_category_1')
        shopinvader_categ = categ.shopinvader_bind_ids
        self.assertEqual(len(shopinvader_categ), 1)
        self.assertEqual(len(shopinvader_categ.shopinvader_child_ids), 3)

    def test_category_child_with_two_lang(self):
        lang = self.install_lang('base.lang_fr')
        self.backend.lang_ids |= lang
        self.backend.bind_all_category()
        categ = self.env.ref('product.product_category_1')
        self.assertEqual(len(categ.shopinvader_bind_ids), 2)
        shopinvader_categ = categ.shopinvader_bind_ids[0]
        self.assertEqual(len(shopinvader_categ.shopinvader_child_ids), 3)
        for binding in categ.shopinvader_bind_ids:
            self.assertEqual(
                binding.shopinvader_parent_id.lang_id, binding.lang_id)
            if binding.lang_id.code == 'fr_FR':
                self.assertEqual(binding.url_key, u'tous/en-vente')
            elif binding.lang_id.code == 'en_US':
                self.assertEqual(binding.url_key, u'all/saleable')

    def test_product_category_with_one_lang(self):
        self.backend.bind_all_product()
        self.backend.bind_all_category()
        product = self.env.ref('product.product_product_4')
        self.assertEqual(len(product.shopinvader_bind_ids), 1)
        shopinvader_product = product.shopinvader_bind_ids
        self.assertEqual(len(shopinvader_product.shopinvader_categ_ids), 3)

    def test_product_category_with_two_lang(self):
        lang = self.install_lang('base.lang_fr')
        self.backend.lang_ids |= lang
        self.backend.bind_all_category()
        self.backend.bind_all_product()
        product = self.env.ref('product.product_product_4')
        self.assertEqual(len(product.shopinvader_bind_ids), 2)
        shopinvader_product = product.shopinvader_bind_ids[0]
        self.assertEqual(len(shopinvader_product.shopinvader_categ_ids), 3)
        for binding in product.shopinvader_bind_ids:
            if binding.lang_id.code == 'fr_FR':
                self.assertEqual(binding.url_key, u'ipad-avec-ecran-retina')
            elif binding.lang_id.code == 'en_US':
                self.assertEqual(binding.url_key, u'ipad-retina-display')

    def test_create_product_binding1(self):
        """
        Test the creation of a product.template.
        During the creation of a new product.template, Odoo create
        automatically a new product.product.
        If the product.template doesn't have a shopinvader.product, we should
        create a new shopinvader.variant (because the product is not published)
        But if it's published, we should create a shopinvader.variant for each
        product.product related to this product.template.
        So each time a product.product is created, we should check if we need
        to create a shopinvader.variant.
        For this test, we create a product.template not published (so no
        shopinvader.variant should be created)
        :return: bool
        """
        product_tmpl_obj = self.env['product.template'].with_context(
            active_test=False)
        product_values = {
            'name': 'Shopinvader t-shirt',
        }
        product_tmpl = product_tmpl_obj.create(product_values)
        self.assertFalse(product_tmpl.shopinvader_bind_ids)
        product_product = product_tmpl.product_variant_ids
        self.assertFalse(product_product.shopinvader_bind_ids)
        return True

    def test_create_product_binding2(self):
        """
        Test the creation of a product.template.
        During the creation of a new product.template, Odoo create
        automatically a new product.product.
        If the product.template doesn't have a shopinvader.product, we should
        create a new shopinvader.variant (because the product is not published)
        But if it's published, we should create a shopinvader.variant for each
        product.product related to this product.template.
        So each time a product.product is created, we should check if we need
        to create a shopinvader.variant.
        For this test, we create a product.template who is not published
        (but with a shopinvader.product related) so the related
        product.product should have a shopinvader.variant.
        :return: bool
        """
        backend = self.backend
        product_tmpl_obj = self.env['product.template'].with_context(
            active_test=False)
        lang = self.env['res.lang']._lang_get(self.env.user.lang)
        product_values = {
            'name': 'Shopinvader t-shirt',
            'shopinvader_bind_ids': [(0, False, {
                'backend_id': backend.id,
                'lang_id': lang.id,
                'active': False,
            })],
        }
        product_tmpl = product_tmpl_obj.create(product_values)
        self.assertTrue(product_tmpl.shopinvader_bind_ids)
        product_product = product_tmpl.product_variant_ids
        self.assertEqual(len(product_product.shopinvader_bind_ids), 1)
        self.assertFalse(product_product.shopinvader_bind_ids.active)
        return True

    def test_create_product_binding3(self):
        """
        Test the creation of a product.template.
        During the creation of a new product.template, Odoo create
        automatically a new product.product.
        If the product.template doesn't have a shopinvader.product, we should
        create a new shopinvader.variant (because the product is not published)
        But if it's published, we should create a shopinvader.variant for each
        product.product related to this product.template.
        So each time a product.product is created, we should check if we need
        to create a shopinvader.variant.
        For this test, we create a product.template who is published
        (with a shopinvader.product related and active = True) so the related
        product.product should have a shopinvader.variant.
        :return: bool
        """
        backend = self.backend
        product_tmpl_obj = self.env['product.template'].with_context(
            active_test=False)
        lang = self.env['res.lang']._lang_get(self.env.user.lang)
        product_values = {
            'name': 'Shopinvader t-shirt',
            'shopinvader_bind_ids': [(0, False, {
                'backend_id': backend.id,
                'lang_id': lang.id,
                'active': True,
            })],
        }
        product_tmpl = product_tmpl_obj.create(product_values)
        self.assertTrue(product_tmpl.shopinvader_bind_ids)
        product_product = product_tmpl.product_variant_ids
        self.assertEqual(len(product_product.shopinvader_bind_ids), 1)
        self.assertFalse(product_product.shopinvader_bind_ids.active)
        return True

    def test_create_product_binding4(self):
        """
        Test the creation of a product.template.
        During the creation of a new product.template, Odoo create
        automatically a new product.product.
        If the product.template doesn't have a shopinvader.product, we should
        create a new shopinvader.variant (because the product is not published)
        But if it's published, we should create a shopinvader.variant for each
        product.product related to this product.template.
        So each time a product.product is created, we should check if we need
        to create a shopinvader.variant.
        For this test, we create a product.template who is published
        (with a shopinvader.product related and active = True) so the related
        product.product should have a shopinvader.variant.
        :return: bool
        """
        backend = self.backend
        color_attribute = self.env.ref("product.product_attribute_2")
        white_attr = self.env.ref("product.product_attribute_value_3")
        black_attr = self.env.ref("product.product_attribute_value_4")
        attr = white_attr | black_attr
        product_tmpl_obj = self.env['product.template'].with_context(
            active_test=False)
        lang = self.env['res.lang']._lang_get(self.env.user.lang)
        product_values = {
            'name': 'Shopinvader t-shirt',
            'shopinvader_bind_ids': [(0, False, {
                'backend_id': backend.id,
                'lang_id': lang.id,
                'active': True,
            })],
        }
        product_tmpl = product_tmpl_obj.create(product_values)
        self.assertTrue(product_tmpl.shopinvader_bind_ids)
        product_product = product_tmpl.product_variant_ids
        self.assertEqual(len(product_product.shopinvader_bind_ids), 1)
        self.assertFalse(product_product.shopinvader_bind_ids.active)
        # Then we add some products attributes (to create some variants)
        product_tmpl.write({
            'attribute_line_ids': [(0, False, {
                'attribute_id': color_attribute.id,
                'value_ids': [(6, False, attr.ids)],
            })],
        })
        self.assertEqual(len(attr), len(product_tmpl.product_variant_ids))
        self.assertEqual(len(attr), len(
            product_tmpl.shopinvader_bind_ids.shopinvader_variant_ids))
        return True

    def test_editing_product_with_sale_manager_user(self):
        # test that product can still be edited without issue
        # when automatically generating a new url
        self.backend.bind_all_product()
        self.user = self.env.ref('base.user_demo')
        self.user.write({'groups_id': [
            (4, self.env.ref('sales_team.group_sale_manager').id)]})
        self.env = self.env(user=self.user)
        product = self.env['product.template'].search([
            ('shopinvader_bind_ids', '!=', False)
            ], limit=1)
        product.name += ' modification'

    def test_multicompany_product(self):
        # Test that default code change with user on company 2
        # changes the url_key on company 1 backend
        self.backend.bind_all_product()
        product_12 = self.env.ref('product.product_product_12')
        shopinvader_product_12 = self.env['shopinvader.product'].search([
            ('record_id', '=', product_12.product_tmpl_id.id),
            ('backend_id', '=', self.backend.id),
        ])
        result = shopinvader_product_12.url_key.find(product_12.default_code)
        self.assertTrue(
            result,
        )
        # If sale_stock module have been installed
        # We need to drop the constraint as at that moment the module
        # is not loaded (shopinvader do not depend on it)
        sale_stock = self.env['ir.module.module'].search([
            ('name', '=', 'sale_stock')])
        if sale_stock.state == 'installed':
            self.cr.execute("""ALTER TABLE res_company
                ALTER COLUMN security_lead
                DROP NOT NULL""")
        # Now we can create the company
        company_2 = self.env['res.company'].create({
            'name': 'Company2',
            'currency_id': self.env.ref('base.EUR').id,
        })
        # Set product shareable between companies
        product_12.company_id = False
        self.env.user.company_id = company_2
        # Change product name to trigger compute
        product_12.write({
            'name': 'Wireless Mouse MultiCompany',
            'default_code': 'product_12_mc'
        })
        result = shopinvader_product_12.url_key.find('product_12_mc')
        self.assertTrue(
            result,
        )

    def test_product_shopinvader_name(self):
        self.backend.bind_all_product()
        product = self.shopinvader_variant.shopinvader_product_id
        product.shopinvader_name = 'Test shopinvader name'
        self.assertEqual(product.shopinvader_display_name, product.name)
        self.backend.use_shopinvader_product_name = True
        self.assertEqual(
            product.shopinvader_display_name, product.shopinvader_name
        )

    def test_product_category_auto_bind(self):
        """
        Test if after a product binding, the category is automatically binded
        too (depending on the configuration).
        :return:
        """
        product = self.env.ref('product.product_product_4').copy()
        # To avoid others products to be binded
        self.env['product.template'].search([
            ('sale_ok', '=', True),
            ('id', 'not in', product.ids),
        ]).write({'sale_ok': False})
        product.write({
            'sale_ok': True,
        })
        categ_obj = self.env['product.category']
        shopinv_categ_obj = self.env['shopinvader.category']
        existing_binded_categs = shopinv_categ_obj.search([])
        categ_grand_parent = categ_obj.create({
            'name': 'Cool grand-parent'
        })
        categ_parent = categ_obj.create({
            'name': 'Strict parent',
            'parent_id': categ_grand_parent.id,
        })
        categ_child = categ_obj.create({
            'name': 'normal child',
            'parent_id': categ_parent.id,
        })
        categs = categ_grand_parent | categ_parent | categ_child
        product.write({
            'categ_id': categ_child.id,
        })
        # New categories shouldn't be binded yet
        self.assertFalse(shopinv_categ_obj.search([
            ('record_id', 'in', categs.ids),
        ]))
        self.backend.write({
            'category_binding_level': 0,
        })
        self.backend.bind_all_product()
        self.assertEquals(existing_binded_categs, shopinv_categ_obj.search([]))
        # New categories shouldn't be binded due to binded level set to 0
        self.assertFalse(shopinv_categ_obj.search([
            ('record_id', 'in', categs.ids),
        ]))
        self.backend.write({
            'category_binding_level': 2,
        })
        self.backend.bind_all_product()
        categ_level2 = categ_child
        categ_level2 |= categ_child.mapped("parent_id")
        shopinv_products = self.env['shopinvader.variant'].search([
            ('backend_id', '=', self.backend.id),
        ])
        categs_binded = shopinv_products.mapped("categ_id")
        categs_binded |= categs_binded.mapped("parent_id")
        existing_binded_categs |= shopinv_categ_obj.search([
            ('record_id', 'in', categs_binded.ids),
        ])
        # Ensure no others categories are binded
        self.assertEquals(existing_binded_categs, shopinv_categ_obj.search([]))
        # categ_child and categ_parent should be binded but not the categ
        # grand_parent due to binding_level defined on 2
        binded_categs = shopinv_categ_obj.search([
            ('record_id', 'in', categs.ids),
        ]).mapped("record_id")
        self.assertIn(categ_parent, binded_categs)
        self.assertIn(categ_child, binded_categs)
        self.assertNotIn(categ_grand_parent, binded_categs)

    def test_product_category_auto_bind_wizard(self):
        """
        Test if after a product binding, the category is automatically binded
        too (depending on the configuration) using the wizard.
        :return:
        """
        wizard_obj = self.env['shopinvader.variant.binding.wizard']
        product = self.env.ref('product.product_product_4').copy()
        wizard_values = {
            'backend_id': self.backend.id,
            'product_ids': [(6, False, product.ids)],
        }
        categ_obj = self.env['product.category']
        shopinv_categ_obj = self.env['shopinvader.category']
        existing_binded_categs = shopinv_categ_obj.search([])
        categ_grand_parent = categ_obj.create({
            'name': 'Cool grand-parent'
        })
        categ_parent = categ_obj.create({
            'name': 'Strict parent',
            'parent_id': categ_grand_parent.id,
        })
        categ_child = categ_obj.create({
            'name': 'normal child',
            'parent_id': categ_parent.id,
        })
        categs = categ_grand_parent | categ_parent | categ_child
        product.write({
            'categ_id': categ_child.id,
        })
        wizard = wizard_obj.create(wizard_values)
        # New categories shouldn't be binded yet
        self.assertFalse(shopinv_categ_obj.search([
            ('record_id', 'in', categs.ids),
        ]))
        self.backend.write({
            'category_binding_level': 0,
        })
        wizard.bind_products()
        self.assertEquals(existing_binded_categs, shopinv_categ_obj.search([]))
        # New categories shouldn't be binded due to binded level set to 0
        self.assertFalse(shopinv_categ_obj.search([
            ('record_id', 'in', categs.ids),
        ]))
        self.backend.write({
            'category_binding_level': 2,
        })
        wizard.bind_products()
        shopinv_products = self.env['shopinvader.variant'].search([
            ('backend_id', '=', self.backend.id),
        ])
        categs_binded = shopinv_products.mapped("categ_id")
        categs_binded |= categs_binded.mapped("parent_id")
        existing_binded_categs |= shopinv_categ_obj.search([
            ('record_id', 'in', categs_binded.ids),
        ])
        # Ensure no others categories are binded
        self.assertEquals(existing_binded_categs, shopinv_categ_obj.search([]))
        # categ_child and categ_parent should be binded but not the categ
        # grand_parent due to binding_level defined on 2
        binded_categs = shopinv_categ_obj.search([
            ('record_id', 'in', categs.ids),
        ]).mapped("record_id")
        self.assertIn(categ_parent, binded_categs)
        self.assertIn(categ_child, binded_categs)
        self.assertNotIn(categ_grand_parent, binded_categs)

    def test_product_url1(self):
        """
        Test the little workflow about shopinvader variants and related URL.
        Expected behaviour:
        - On the unbind (active = False) => URL should be a redirect to a
        category who doesn't have children
        - On the bind (active = True) => Existing redirect URL should be
        deleted and new one should be re-generated
        For this case, we test a normal workflow: url should be related to
        the category (during unbind) and then we re-bind this product
        and new url should be generated
        :return:
        """
        bind_variant_model = self.env['shopinvader.variant.binding.wizard']
        bind_category_model = self.env['shopinvader.category.binding.wizard']
        product_tmpl_obj = self.env['product.template']
        categ = self.env.ref("product.product_category_all")
        categ_wizard = bind_category_model.create({
            'backend_id': self.backend.id,
            'product_category_ids': [(6, 0, categ.ids)]
        })
        categ_wizard.action_bind_categories()
        domain = [
            ('record_id', '=', categ.id),
            ('backend_id', '=', self.backend.id),
        ]
        bind_categ = self.env['shopinvader.category'].search(domain)
        # For this case, the category should have children
        if bind_categ.shopinvader_child_ids:
            bind_categ.shopinvader_child_ids.unlink()
        product_values = {
            'name': 'Shopinvader Rocket',
            'categ_id': categ.id,
        }
        product_tmpl = product_tmpl_obj.create(product_values)
        product_product = product_tmpl.product_variant_ids

        product_wizard = bind_variant_model.create({
            'backend_id': self.backend.id,
            'product_ids': [(6, 0, product_product.ids)]
        })
        product_wizard.bind_products()
        bind_product = self.env['shopinvader.variant'].search([
            ('record_id', '=', product_product.id),
            ('backend_id', '=', self.backend.id),
        ])
        self.assertIn(bind_categ, bind_product.shopinvader_categ_ids)
        urls = bind_product.url_url_ids
        self.assertEqual(
            urls.mapped("model_id"), bind_product.shopinvader_product_id)
        bind_product._unbind()
        self.assertEqual(urls.mapped("model_id"), bind_categ)
        bind_product._bind()
        self.assertFalse(bool(urls.exists()))
        urls = bind_product.url_url_ids
        self.assertEqual(
            urls.mapped("model_id"), bind_product.shopinvader_product_id)

    def test_product_url2(self):
        """
        Test the little workflow about shopinvader variants and related URL.
        Expected behaviour:
        - On the unbind (active = False) => URL should be a redirect to a
        category who doesn't have children
        - On the bind (active = True) => Existing redirect URL should be
        deleted and new one should be re-generated
        For this case, we simulate a normal workflow with different categories
        :return:
        """
        bind_variant_model = self.env['shopinvader.variant.binding.wizard']
        bind_category_model = self.env['shopinvader.category.binding.wizard']
        product_tmpl_obj = self.env['product.template']
        categ_all = self.env.ref("product.product_category_all")
        categ2 = self.env.ref("product.product_category_2")
        categs = categ_all | categ2
        categ_wizard = bind_category_model.create({
            'backend_id': self.backend.id,
            'product_category_ids': [(6, 0, categs.ids)]
        })
        categ_wizard.action_bind_categories()
        domain = [
            ('record_id', '=', categ_all.id),
            ('backend_id', '=', self.backend.id),
        ]
        bind_categ_all = self.env['shopinvader.category'].search(domain)
        domain = [
            ('record_id', '=', categ2.id),
            ('backend_id', '=', self.backend.id),
        ]
        bind_categ2 = self.env['shopinvader.category'].search(domain)
        product_values = {
            'name': 'Shopinvader Rocket',
            'categ_id': categ2.id,
        }
        product_tmpl = product_tmpl_obj.create(product_values)
        product_product = product_tmpl.product_variant_ids

        product_wizard = bind_variant_model.create({
            'backend_id': self.backend.id,
            'product_ids': [(6, 0, product_product.ids)]
        })
        product_wizard.bind_products()
        bind_product = self.env['shopinvader.variant'].search([
            ('record_id', '=', product_product.id),
            ('backend_id', '=', self.backend.id),
        ])
        self.assertIn(bind_categ_all, bind_product.shopinvader_categ_ids)
        self.assertIn(bind_categ2, bind_product.shopinvader_categ_ids)
        urls = bind_product.url_url_ids
        self.assertEqual(
            urls.mapped("model_id"), bind_product.shopinvader_product_id)
        bind_product._unbind()
        self.assertEqual(urls.mapped("model_id"), bind_categ2)
        bind_product._bind()
        self.assertFalse(bool(urls.exists()))
        urls = bind_product.url_url_ids
        self.assertEqual(
            urls.mapped("model_id"), bind_product.shopinvader_product_id)
