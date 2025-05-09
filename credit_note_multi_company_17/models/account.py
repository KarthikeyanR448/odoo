from odoo import api, fields, models
from odoo.tools.float_utils import float_compare

class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Account Move'

    credit_note_count = fields.Integer(
        compute="_compute_credit_note_count",
        string="Credit Notes",
    )

    @api.depends("name")
    def _compute_credit_note_count(self):
        """Compute the number of credit notes for each invoice"""

        for invoice in self:
            invoice.credit_note_count = len(
                invoice.search([("reversed_entry_id", "=", invoice.id)])
            )

    def _get_matching_multi_company_credit_notes(self, client_order_ref, company_id, invoice_type):
        """Get draft credit notes from other companies that match the current one.

        Args:
            client_order_ref (str): Client order reference.
            company_id (int): Current company ID.
            invoice_type (str): Type of the invoice to search for.

        Returns:
            list(account.move): Matching credit notes from other companies.
        """
        domain = [
            ('ref', '=', client_order_ref),
            ('company_id', '!=', company_id),
            ('move_type', '=', invoice_type),
        ]

        candidate_notes = self.env['account.move'].sudo().search(domain).filtered(
            lambda m: float_compare(m.amount_total, self.amount_total, precision_digits=2) == 0
        )#NOTE: precision digits or rounding should be used if any issue.

        matching_notes = []
        for note in candidate_notes:
            if all(
                cl.product_id.id == ml.product_id.id and
                cl.quantity == ml.quantity and
                cl.price_total == ml.price_total
                for cl, ml in zip(self.invoice_line_ids, note.invoice_line_ids)
            ):#NOTE: use sorted if product sequence are different
                matching_notes.append(note)

        return matching_notes

    def action_post(self):
        """Post the credit note and post matching notes in other companies."""
        res = super().action_post()

        if (
            self.ref and
            self.move_type == "out_refund" and
            not self._context.get('multi_company_post')
        ):
            matching_notes = self._get_matching_multi_company_credit_notes(
                client_order_ref=self.ref,
                company_id=self.company_id.id,
                invoice_type='out_refund',
            )

            for note in matching_notes:
                if note.state == 'draft':
                    note.with_context(multi_company_post=True).action_post()
                    break

        return res

    def button_cancel(self):
        """Cancel the credit note and cancel matching notes in other companies."""
        res = super().button_cancel()

        if (
            self.ref and
            self.move_type == "out_refund" and
            not self._context.get('multi_company_cancel')
        ):
            matching_notes = self._get_matching_multi_company_credit_notes(
                client_order_ref=self.ref,
                company_id=self.company_id.id,
                invoice_type='out_refund',
            )

            for note in matching_notes:
                if note.state == 'draft':
                    note.with_context(multi_company_cancel=True).button_cancel()
                    break

        return res
    
    def action_open_credit_note(self):
        """Credit note smart button"""

        tree = self.env.ref("account.view_out_invoice_tree").id
        form = self.env.ref("account.view_move_form").id

        return {
            "view_mode": "tree,form",
            "res_model": "account.move",
            "views": [[tree, "list"], [form, "form"]],
            "type": "ir.actions.act_window",
            "domain": "[['reversed_entry_id','='," + str(self.id) + "]]",
            "name": "Credit Notes",
            "target": "self",
        }

