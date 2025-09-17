from odoo import fields, models

class ResUsers(models.Model):
    _inherit = 'res.users'

    # Properties assigned to this user, only those still available
    property_ids = fields.One2many(
        'estate.property',
        'salesperson_id',
        domain=[('state', 'not in', ['sold', 'canceled'])],
        string='Properties'
    )
