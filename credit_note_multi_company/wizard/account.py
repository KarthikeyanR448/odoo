from odoo import models
from odoo.exceptions import UserError

class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'
    _description = 'Account Move Reversal'

    def _is_multi_company_order(self, invoice):
        """Check if a sales order with the invoice's ref exists in multiple companies."""
        
        if not invoice.ref:
            return False
        sales = self.env['sale.order'].sudo().search([('client_order_ref', '=', invoice.ref)])
        return len(sales) >= 2

    def _get_multi_company_invoices(self, client_order_ref, company_id, invoice_type):
        """Retrieve invoices with the same ref but from other companies."""
        
        domain = [
            ('ref', '=', client_order_ref),
            ('company_id', '!=', company_id),
            ('move_type', '=', invoice_type)
        ]
        return self.env['account.move'].search(domain)

    def create_credit_note_on_multi_company(self, invoice, form, product_line_vals):
        """Create credit note in another company when a refund is created in current company."""
        
        if not invoice.ref:
            return self.env['account.move']

        self = self.sudo()
        multi_cmp_invoices = self._get_multi_company_invoices(invoice.ref, invoice.company_id.id, 'out_invoice')

        print(multi_cmp_invoices,invoice.ref,'rrrrrrrrrrrrrr')
        if not multi_cmp_invoices:
            return self.env['account.move']

        multi_invoice = multi_cmp_invoices[0]  # Assume one matching invoice
        product_line_vals = [
            line for line in product_line_vals
            if line['line_ids'][0][2].get('account_id')
        ]

        # Map product to account & tax details from other company's invoice
        product_account_map = {
            line.product_id.id: {
                'account_id': line.account_id.id,
                'tax_ids': line.tax_ids.ids
            }
            for line in multi_invoice.invoice_line_ids
        }

        # Inject account and tax IDs into the refund lines
        for line in product_line_vals[0]['line_ids']:
            product_data = product_account_map.get(line[2]['product_id'], {})
            line[2]['account_id'] = product_data.get('account_id')
            line[2]['tax_ids'] = product_data.get('tax_ids')

        if not product_line_vals:
            return self.env['account.move']
        print(multi_invoice,"LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL")

        # Reverse the invoice
        refund = multi_invoice._reverse_moves(default_values_list=[{
            'ref': invoice.ref,
            'name': '/',
            'date': form.date or False,
            'invoice_date': form.date or False,
            'line_ids': product_line_vals[0]['line_ids'],
        }], cancel=False)
        print(refund,'refund----------------==================')

        # Update reversed line details: price & reason
        for line,refund_line in zip(refund.line_ids.filtered(lambda l:l.product_id),
                                    form.account_move_reversal_line.filtered(
                                        lambda refund_product: refund_product.select_product)
                                    ):
                    if refund_line.product_id.id == line.product_id.id:
                        line['credit_reason_id'] = refund_line.reason_id.id
                        line['price_unit'] = (refund_line.price_unit/100)*refund_line.refund_percent


        return refund

    def reverse_moves(self, is_modify=False):
        """Override to handle multi-company refunds."""
        res = super().reverse_moves(is_modify=is_modify)

        for form in self:
            for line in form.account_move_reversal_line:
                if line.select_product and line.product_id.type != 'service' and not line.reason_id:
                    raise UserError("Provide a reason to refund non-service products.")

            for invoice in form.move_ids:
                print(invoice,'iiiiiiiiiiiiiiiiiiiiii')
                if self._is_multi_company_order(invoice):
                    print("MMMMMMMMMMMM CCCCCCCCCCCCCCCCCCCCCCCCCCCCCC")
                    product_vals = self._prepare_default_reversal(invoice)
                    print(product_vals,'vvvvvvvvvvvvvvvv')
                    self.create_credit_note_on_multi_company(invoice, form, [product_vals])

        return res

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = 'Account Payment Register'

    def get_line_ids(self, note):
        """Filters required line ids for the payment in another company credit note"""

        line_ids = note.line_ids.filtered(lambda line:line.account_type in ['asset_receivable', 'liability_payable']
                                                  and not line.currency_id.is_zero(line.amount_residual_currency)
                                                  and not line.company_currency_id.is_zero(line.amount_residual))
        return line_ids
    
    def get_invoice_payment(self, note):
        """Search the invoice payment in another company credit note"""

        domain = [
            ("ref", "=", note.reversed_entry_id.name),
            ("company_id" ,"=", note.company_id.id),
            ]
        
        return note.env["account.payment"].sudo().search(domain)

    def get_payment_values(self, note):
        """Payment values to create credit note payment"""

        invoice_payment = self.get_invoice_payment(note=note)
        line_ids = self.get_line_ids(note=note)

        return {
            'amount': note.amount_total,
            'payment_type': 'outbound',
            'company_id': note.company_id.id,
            'journal_id': invoice_payment.journal_id.id,
            'partner_type': 'customer',
            'payment_method_line_id': invoice_payment.payment_method_line_id.id,
            'payment_date': note.invoice_date,
            'communication': note.ref,
            'line_ids': line_ids.ids,
            }

    def action_create_payments(self):
        """Create payment in another company when a payment is created in the current company"""
        res = super(AccountPaymentRegister, self).action_create_payments()

        self = self.sudo()
        for credit_note in self.line_ids.mapped('move_id'):
            matching_credit_notes = credit_note._get_matching_multi_company_credit_notes(
                    client_order_ref=credit_note.ref,
                    company_id=self.company_id.id,
                    invoice_type='out_refund',
                )
            if matching_credit_notes:
                note = matching_credit_notes[0].sudo().with_company(matching_credit_notes[0].company_id)

                payment_vals = self.get_payment_values(note=note)
                
                payment = note.env["account.payment.register"].create(payment_vals)
                payment.with_context(can_edit_wizard=False,
                                     dont_redirect_to_payments=True,
                                     active_id=note.id,
                                     active_ids=note.line_ids.ids,
                                     )._create_payments()

        return res
