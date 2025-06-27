# sheet names
PIZZA_SHEET = "Pizza"
PASTA_SHEET = "Pasta"
DIFFERENCES_SHEET = "Differences"
AVERAGES_SHEET = "Averages"

# For testing purposes, different sheet names
# PIZZA_SHEET = "Pizza (Test)"
# PASTA_SHEET = "Pasta (Test)"
# DIFFERENCES_SHEET = "Differences (Test)"
# AVERAGES_SHEET = "Averages (Test)"

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
COL_COUNT = "Count"
COL_AVERAGE = "Average"
COL_LOWEST = "Lowest"
COL_HIGHEST = "Highest"

PIZZA_HEADER = [
    COL_RESTAURANT,
    COL_TYPE,
    COL_NAME,
    COL_PRICE,
    COL_DESCRIPTION,
]

PASTA_HEADER = [
    COL_RESTAURANT,
    COL_TYPE,
    COL_NAME,
    COL_PRICE,
    COL_DESCRIPTION,
]

DIFFERENCES_HEADER = [
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

AVERAGES_HEADER = [
    COL_RESTAURANT,
    COL_TYPE,
    COL_COUNT,
    COL_AVERAGE,
    COL_LOWEST,
    COL_HIGHEST,
]
