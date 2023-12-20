# Sanger Institute Software Developer Test Assessment

## 1. Modeling database scheme

### Samples table
- A sample will have one sample_id allocated by Sanger which is a non-zero positive integer.
- The sample_id allocated by Sanger must be unique across ALL our samples.

So sample_id will be the primary key

- A sample will have one customer_sample_name 
- The customer_sample_name may not be unique across ALL our samples.

So customer_sample_name will not be primary key and will be included in samples table

Tubes do not have a separate properties, so they could be stored in samples table. 
So, we add UNIQUE tube_barcode in samples table.

### Well table

- Plates have 96 wells.
- Wells are arranged in a grid made of 12 columns and 8 rows.
- Wells are labelled like “A1”, “A2” through to “H12”. The well label is made from row ‘A’ through to ‘H’ and columns ‘1’ through to ‘12’.

There are no so much difference how to store position (enum, char, or tinyint), but 
I decided to store wells position as integers because:
- performance, storage optimisation (using tinyint)
- more way to extend it in future

But this is a point to discuss. 
- Do we have existing databases that stores values in specific format?

Separate plate table not required because there are not specific attributes on plates

All the wells that have something inside will be recorded in database.
Not filled wells will not be recorded


Also: 
- tube_barcode should be indexed to optimize contained sample query

Other assumptions that are not obvious from task description:
- Tubes can be reused after moving sample from them (any sample can be put there)
- tube_transfer could be performed to "not recorded" tube, (which was not receipt)
