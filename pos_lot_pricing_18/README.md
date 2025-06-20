# Feature Description
The module creates LOT for a product with sale price for each LOT specified in Purchase Order to show the LOT and sale price for respective LOT number in POS.

## Key Benefits:
1. It allows to choose required LOT from POS view to select the required LOT number with the sale price.
2. LOT number is generated with sale price, created with chosen pricelist based on its configuration.

## How It Works:
1. After confirming the Purchase Order with the LOT product, generate the LOT number in Purchase Receipt with the specific pricelist to calculate.
2. It will create LOT with sale price and that is shown in POS screen to select specific LOT with Price.
3. The chosen sale price amount is used to create pos order records.

## Use Cases:
* To choose specific LOT number with required sale price.

## Technical Specifications:
* Only LOT number is displayed with sale price in POS.

## Setup
1. Generate LOT number in Purchase Receipt by choosing the pricelist.
2. Select the required product displayed with LOT number and sale price.
