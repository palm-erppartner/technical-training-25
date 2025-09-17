from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_is_zero, float_compare

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate property"

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
    garden = fields.Boolean()
    garden_area = fields.Integer(string="Garden Area (sqm)")
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
    property_type_id = fields.Many2one("estate.property.type")
    salesperson_id = fields.Many2one("res.users", string="Salesperson", default=lambda self: self.env.user,)
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False,)
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers",)
    total_area = fields.Integer(string="Total Area (sqm)", compute="_compute_total_area",)
    best_price = fields.Float(string="Best Offer", compute="_compute_best_price",)

    _sql_constraints = [
        (
            "check_expected_price",
            "CHECK(expected_price > 0)",
            "The expected price must be strictly positive.",
        ),
        (
            "check_selling_price",
            "CHECK(selling_price >= 0)",
            "The selling price must be positive.",
        ),
    ]

    
    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            living = record.living_area or 0
            garden = record.garden_area or 0
            record.total_area = living + garden

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for property in self:
            if property.offer_ids:
                property.best_price = max(property.offer_ids.mapped("price"))
            else:
                property.best_price =0.0

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = False

    def action_mark_sold(self):
        for record in self:
            if record.state == "cancelled":
                raise UserError("A cancelled property cannot be sold.")
            record.state = "sold"
        return True

    def action_cancel_property(self):
        for record in self:
            if record.state == "sold":
                raise UserError("A sold property cannot be cancelled.")
            record.state = "cancelled"
        return True

    @api.constrains("selling_price", "expected_price")
    def _check_selling_price(self):
        for property in self:
            if (
                not float_is_zero(property.selling_price, precision_rounding=0.01)
                and float_compare(
                    property.selling_price,
                0.9 * property.expected_price,
                precision_rounding=0.01,
                ) < 0
            ):
                raise ValidationError(
                    _("The selling price should not be lower than 90% of the expected price")
                )
    