from odoo import _, api, fields, models
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"

    price = fields.Float(string="Price")

    # Do not copy the status when duplicating an offer
    status = fields.Selection(
        selection=[("accepted", "Accepted"), ("refused", "Refused")],
        string="Status",
        copy=False,
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        required=True,
    )

    property_id = fields.Many2one(
        "estate.property",
        string="Property",
        required=True,
    )

    validity = fields.Integer(string="Validity (days)", default=7)

    date_deadline = fields.Date(
        string="Deadline",
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
        store=True,
    )

    _sql_constraints = [
    (
        "check_offer_price",
        "CHECK(price > 0)",
        "An offer price must be strictly positive.",
    ),
]

    @api.depends("validity", "create_date")
    def _compute_date_deadline(self):
        for offer in self:
            base_dt = offer.create_date or fields.Datetime.now()
            offer.date_deadline = (base_dt + relativedelta(days=offer.validity)).date()

    def _inverse_date_deadline(self):
        for offer in self:
            if offer.date_deadline:
                base_date = (offer.create_date or fields.Datetime.now()).date()
                offer.validity = (offer.date_deadline - base_date).days
            else:
                offer.validity = 0

    def action_accept_offer(self):
        for offer in self:
            if offer.property_id.state == "cancelled":
                raise UserError("Cannot accept an offer for a cancelled property.")
            offer.status = "accepted"
            offer.property_id.selling_price = offer.price
            offer.property_id.buyer_id = offer.partner_id
        return True

    def action_refuse_offer(self):
        for offer in self:
            offer.status = "refused"
        return True

    @api.model_create_multi
    def create(self, vals_list):
        # Validate each payload before creating anything
        for vals in vals_list:
            prop = self.env["estate.property"].browse(vals["property_id"])
            if prop.offer_ids:
                best = max(prop.offer_ids.mapped("price"))
                if vals.get("price", 0.0) <= best:
                    raise UserError(
                        _("The offer must be higher than %s") % best
                    )

        # Create all offers in one go
        records = super().create(vals_list)

        # Update related properties' state
        for offer in records:
            offer.property_id.state = "offer_received"

        return records
