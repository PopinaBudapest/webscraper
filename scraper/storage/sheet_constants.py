# sheet names
PRODUCTS_SHEET = "Products"
DIFFERENCES_SHEET = "Differences"
LAST_RUN_SHEET = "Last Run"

# For testing purposes, we use different sheet names
# PRODUCTS_SHEET = "Products_Test"
# DIFFERENCES_SHEET = "Differences_Test"

# column names
COL_DATE = "Date"
COL_RESTAURANT = "Restaurant"
COL_TYPE = "Type"
COL_NAME = "Name"
COL_DESCRIPTION = "Description"
COL_PRICE = "Price"
COL_NEW_PRICE = "New Price"
COL_OLD_PRICE = "Old Price"
COL_NEW_DESCRIPTION = "New Description"
COL_OLD_DESCRIPTION = "Old Description"
COL_COMMENT = "Comment"

# header order for writes
PRODUCT_HEADERS = [
    COL_DATE,
    COL_RESTAURANT,
    COL_TYPE,
    COL_NAME,
    COL_PRICE,
    COL_DESCRIPTION,
]

DIFFERENCE_HEADERS = [
    COL_DATE,
    COL_RESTAURANT,
    COL_TYPE,
    COL_NAME,
    COL_OLD_PRICE,
    COL_NEW_PRICE,
    COL_OLD_DESCRIPTION,
    COL_NEW_DESCRIPTION,
    COL_COMMENT,
]
