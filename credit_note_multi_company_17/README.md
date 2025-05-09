# Feature Description
The credit note multi-company creates a duplication in the another company when progress in credit notes like create, confirm, cancel, register payment is done.

## Key Benefits:
1. It allows companies to manage credit notes across different entities from a single platform, ensuring consistency and reducing manual errors.
2. Refunds and adjustments can be processed seamlessly across multiple companies, reducing administrative workload.

## How It Works:
1. Once the Invoice is confirmed, it allows to create a credit note for the invoice.
2. While creating a credit note in one company it finds the same invoice with the same reference number in the other company and creates a credit note for that invoice.
3. In confirming or cancelling the credit note or register payment. If a same reference credit note is found in another company then it performs the same action in the another company.

## Use Cases:
* Reduces same action multiple times for each company.

## Technical Specifications:
* This feature only allows credit note to perform in multiple companies.

## Setup
1. Specify customer reference in the Sale Order and Invoice.
2. Set Product if dropship and its configurations.
3. Perform usual actions like creating credit note, confirming, register payment or cancellation.
