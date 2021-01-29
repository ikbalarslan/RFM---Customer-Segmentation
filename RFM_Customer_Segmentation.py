# Variables
# InvoiceNo: Invoice number. The unique number for each transaction.
# IMPORTANT NOTE: If İnvoiceNo code starts with C, it indicates that the transaction has been canceled.
# StockCode: Product code. Unique number for each product.
# Description: Product name
# Quantity: Number of items. It expresses how many products in the invoices are sold.
# InvoiceDate: Invoice date and time.
# UnitPrice: Product price (in Pounds)
# CustomerID: Unique customer number
# Country: Country name. The country where the customer lives.


# Customer Segmentation with RFM

###############################################################
# Data Understanding
###############################################################

import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
# pd.set_option('display.float_format', lambda x: '%.5f' % x)


df_ = pd.read_excel("WEEK 3/online_retail_II.xlsx", sheet_name="Year 2010-2011")
df = df_.copy()
df.head()
df = df[~df["Invoice"].str.contains("C", na=False)]


# What is the unique product number?
df["Description"].nunique()

# How many of which products are there?
df["Description"].value_counts().head()

# What is the mostly ordered product? (sorted)
df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()

#How many invoices are there in total?
df["Invoice"].nunique()

# How much money has been earned per invoice?
# Here is the important point : There are some transactions have been canceled.
df["TotalPrice"] = df["Quantity"] * df["Price"]

# Which are the most expensive products?
df.sort_values("Price", ascending=False).head()

# How many orders came from which country?
df["Country"].value_counts()

# How much money was earned from which country?
df.groupby("Country").agg({"TotalPrice": "sum"}).sort_values("TotalPrice", ascending=False).head()


df["TotalPrice"] = df["Quantity"] * df["Price"]


###############################################################
# Data Preparation
###############################################################

#Total missing values:
df.isnull().sum()

df.dropna(inplace=True)

df.describe([0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99]).T


###############################################################
# Calculating RFM Metrics
###############################################################

# Recency, Frequency, Monetary

# Recency: The time since the customer's last purchase

# Today date - Last purchase
# Last purchase date:
df["InvoiceDate"].max()


today_date = dt.datetime(2011, 12, 11)

rfm = df.groupby('Customer ID').agg({"InvoiceDate": lambda date: (today_date- date.max()).days,
                                     "Invoice": lambda num: num.nunique(),
                                     "TotalPrice" : lambda TotalPrice: TotalPrice.sum()})


rfm.columns = ['Recency', 'Frequency', 'Monetary']

# Even if the frequency is greater than 0, situations where the monetary value is not greater than 0 are observed:
rfm[~((rfm["Monetary"]) > 0 & (rfm["Frequency"] > 0))]

rfm = rfm[(rfm["Monetary"]) > 0 & (rfm["Frequency"] > 0)]

###############################################################
# Calculating RFM Scores
###############################################################

# Recency

rfm["RecencyScore"] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])

# Frequency

rfm["FrequencyScore"] = pd.qcut(rfm['Frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

# Monetary
rfm["MonetaryScore"] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])

# Values are converted to string, written together and assigned to the new RFM_SCORE variable:
rfm["RFM_SCORE"] = (rfm['RecencyScore'].astype(str) +
                    rfm['FrequencyScore'].astype(str) +
                    rfm['MonetaryScore'].astype(str))


###############################################################
# Naming & Analysing RFM Segments
###############################################################

seg_map = {
    r'[1-2][1-2]': 'Hibernating',
    r'[1-2][3-4]': 'At_Risk',
    r'[1-2]5': 'Cant_Loose',
    r'3[1-2]': 'About_to_Sleep',
    r'33': 'Need_Attention',
    r'[3-4][4-5]': 'Loyal_Customers',
    r'41': 'Promising',
    r'51': 'New_Customers',
    r'[4-5][2-3]': 'Potential_Loyalists',
    r'5[4-5]': 'Champions'}

rfm

rfm['Segment'] = rfm['RecencyScore'].astype(str) + rfm['FrequencyScore'].astype(str)
rfm['Segment'] = rfm['Segment'].replace(seg_map, regex=True)


df[["Customer ID"]].nunique()
rfm[["Segment", "Recency", "Frequency", "Monetary"]].groupby("Segment").agg(["mean", "count"])

#####################################
# Choose 3 different segment to obtain mean RFM values and interpret the reults:
#####################################

#Cant_Loose, Loyal_Customers and Potential_Loyalists are chosen to evaluate:

# 1. YOL
rfm[rfm["Segment"] == "Loyal_Customers"].describe().T
rfm[rfm["Segment"] == "Potential_Loyalists"].describe().T
rfm[rfm["Segment"] == "Cant_Loose"].describe().T

# 2. YOL
fancy = ["Loyal_Customers", "Potential_Loyalists", "Cant_Loose"]

new_rfm = rfm[rfm["Segment"].isin(fancy)]

new_rfm[["Segment", "Recency", "Frequency", "Monetary"]].groupby("Segment").agg(
    ["mean", "count", "median"])

#####################################
# How to obtain xlsx form of the Loyal Customers:
#####################################

rfm[rfm["Segment"] == "Loyal_Customers"].head()
rfm[rfm["Segment"] == "Loyal_Customers"].index

new_df = pd.DataFrame()
new_df["Loyal_Customers"] = rfm[rfm["Segment"] == "Loyal_Customers"].index

new_df.to_excel("LoyalCustomers.xlsx")


