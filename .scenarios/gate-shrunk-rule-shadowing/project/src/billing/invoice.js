import { signToken } from '../auth/internal/token.js';

export function invoiceLink(invoiceId) {
    return `/invoices/${invoiceId}?token=${signToken({ invoiceId })}`;
}
