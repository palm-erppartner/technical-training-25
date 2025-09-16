from odoo import fields, models

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "estate.property"

    name = fields.Char(required=True, default="Unknown")
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=lambda self: fields.Date.add(fields.Date.today(), months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default = 2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean(string="Garden Area (sqm)")
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        [("north", "North"), ("south", "South"), ("east", "East"), ("west", "West")])
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
            ("new", "New"), ("offer_received", "Offer received"), ("offer_accepted", "Offer accepted"), ("sold", "Sold"), ("cancelled", "Cancelled")
        ],
        default="new",
        copy=False,
        required=True
    )