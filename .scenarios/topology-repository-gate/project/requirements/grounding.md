# Invoicing self-service: requirements grounding

Version 3, accepted on 2026-10-02 by the product owner. This file is the
canonical requirement source. `records.yaml` and `edges.yaml` normalize it and
add no meaning.

## Problem

An account owner who needs a past invoice or a monthly statement for
bookkeeping cannot get it without contacting support.

Done when an account owner can obtain any invoice or statement issued to their
account without contacting support.

Not the problem: changing what an invoice or a statement contains, credit
notes, or access for anyone other than the account owner.

## Scopes

- `invoices`: past invoices of an account.
- `statements`: monthly statements of an account.
- `document-store`: shared foundation that keeps issued documents retrievable.

## Requirements

### document-archive

Actor: account owner
Must be able to: rely on every issued invoice and statement staying retrievable
as issued for seven years.
Complete when:
- every document issued in the last seven years can be fetched by its identifier;
- a fetched document is identical to the document that was issued.
Basis: authoritative
Source or evidence: finance policy FP-12, tax retention rule
Priority: must

### invoice-download

Actor: account owner
Must be able to: obtain any invoice issued to their account.
Complete when:
- the account owner can list the invoices issued to the account;
- the account owner can download each listed invoice as it was issued.
Relies on: document-archive keeps every issued invoice retrievable as issued.
Basis: evidenced
Source or evidence: support tickets, third-quarter count
Priority: must

### statement-download

Actor: account owner
Must be able to: obtain any monthly statement issued to their account.
Complete when:
- the account owner can list the statements issued to the account;
- the account owner can download each listed statement as it was issued.
Relies on: document-archive keeps every issued statement retrievable as issued.
Basis: evidenced
Source or evidence: support tickets, third-quarter count
Priority: should

### owner-only-access

Actor: account owner
Must be able to: rely on the invoices and statements of the account being
available to the account owner only.
Holds across: invoices, statements
Complete when:
- a signed-in user who is not the account owner is refused each document;
- the account owner is refused none of the documents of the account.
Basis: authoritative
Source or evidence: customer contract, clause 9
Priority: must
