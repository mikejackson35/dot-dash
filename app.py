import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO

st.set_page_config(page_title='Awake Sales',
                   page_icon=":bar_chart:",
                   layout='wide'
)

# ---- PULL IN DATA ----
@st.cache
def get_data_from_csv():
    df = pd.read_csv('all_sales_data.csv')
    return df
df = get_data_from_csv()

### MASTER DATA ###
all_sales = df.copy()

# invoice date cleanup
all_sales['Invoice Date'] = pd.to_datetime(all_sales['Invoice Date'])
all_sales['Invoice Date'] = all_sales['Invoice Date'].dt.normalize()
all_sales['Invoice Date'] = all_sales['Invoice Date'].dt.floor('D')

# --- FILTERS AND SIDEBAR ----
# variables
year = st.sidebar.multiselect(
    "Year:",
    options=all_sales['Invoice Date'].dt.year.unique(),
    default=all_sales['Invoice Date'].dt.year.unique(),
)

segment = st.sidebar.multiselect(
    "Market Segment:",
    options=all_sales['Market Segment'].unique(),
    default=all_sales['Market Segment'].unique(),
)

# QUERY THE DATEFRAME BASED ON FILTER SELECTIONS
df_selection = all_sales[
    (all_sales['Invoice Date'].dt.year.isin(year)) &
    (all_sales['Market Segment'].isin(segment))
    ]

## DOWNLOAD CSV BUTTON ###
@st.cache
def convert_df(df):
    # preventing computation on every rerun
    return df_selection.to_csv().encode('utf-8')

csv = convert_df(df_selection)

st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='awake_sales_output.csv',
    mime='text/csv',
)

# display descriptive subheader and table
st.markdown(f"raw data  -  {len(df_selection)} rows")
table_to_display = df_selection[['Invoice Date', 'Sale Origin', 'Market Segment', 'Parent Customer', 'Customer', 'Customer Order Number','Item Full Description','Dollars']].sort_values(by='Invoice Date').reset_index(drop=True)

# df_selection['Invoice Date'] = pd.to_datetime(df_selection['Invoice Date'])
# df_selection['Invoice Date'] = df_selection['Invoice Date'].dt.normalize()
# df_selection['Invoice Date'] = df_selection['Invoice Date'].dt.floor('D')

st.dataframe(table_to_display.round(2))

# ---- MAINPAGE ----
st.title("Awake Sales")
# st.title(":bar_chart: Awake Sales")
st.markdown("##")

# ---- TOP KPI's Row ----
total_sales = int(df_selection['Dollars'].sum())
mean_sales = int(df_selection['Dollars'].mean())
customer_count = int(df_selection['Customer'].nunique())

logo, left_column, middle_column, right_column = st.columns([.5,1.5,1.5,1.5])
with logo:
    st.image("Nevil.png", width=100)
with left_column:
    st.subheader('Total Sales')
    st.subheader(f"US $ {total_sales:,}")
with middle_column:
    st.subheader('Avg Sales per<br>Customer')
    st.subheader(f"{mean_sales:,}")
with right_column:
    st.subheader('Count of<br>Customers')
    st.subheader(F"{customer_count:,}")

# METRICS

# sales_23 = df_selection[df_selection['Invoice Date'].dt.year == 2023].Dollars.sum()
# sales_22 = df_selection[df_selection['Invoice Date'].dt.year == 2022].Dollars.sum()
# yoy_diff_usd = int(sales_23-sales_22)
# yoy_diff_perc = round(int(sales_23-sales_22) / sales_22,2)

# st.metric(label='YoY Chg', value=yoy_diff_usd, delta = yoy_diff_perc)



# line divider
st.markdown("---")


# ---- CREATE 2 GRAPHS ----
seg_sales = df_selection.groupby('Market Segment',as_index=False)['Dollars'].sum()
fig_seg_sales = px.bar(
    seg_sales.sort_values(by = 'Dollars',ascending=False),
    x='Dollars',
    y='Market Segment',
    orientation = 'h',
    title = "<b>by Market Segment</b>",
    template = 'plotly_white',
    color='Market Segment',
    labels={'Market Segment':'',
            'Dollars':'<b>$USD</b>'},
    # width=800
).update_layout(showlegend=False)

sales_per_day = df_selection.groupby(pd.Grouper(freq='W', key='Invoice Date'))['Dollars'].sum()
fig_sales_per_day = px.line(
    sales_per_day,
    x=sales_per_day.index,
    y='Dollars',
    title='<b>Weekly Sales</b>',
    template = 'plotly_white',
    labels={'Invoice Date':'',
            'Dollars':'<b>$USD</b>'}
)

# ---- CREATE TWO COLUMNS AND PLACE GRAPHS ----
left_column, right_column = st.columns([2,1])
left_column.plotly_chart(fig_sales_per_day, theme = 'streamlit', use_container_width=True)
right_column.plotly_chart(fig_seg_sales, theme = 'streamlit', use_container_width=True)

# ---- CREATE ROW 2 MORE GRAPHS ----
dist_sales = df_selection.groupby('Customer',as_index=False)['Dollars'].sum()
fig_dist_sales = px.bar(
    dist_sales.sort_values(by = 'Dollars',ascending=False)[:20],
    x='Customer',
    y='Dollars',
    title='<b>Sales by Distributor</b>',
    height=525,
    template = 'plotly_white',
    labels={'Customer':'',
            'Dollars':'<b>$USD</b>'}
)

parent_sales = df_selection.groupby(['Parent Customer','Market Segment'],as_index=False)['Dollars'].sum()
fig_parent_sales = px.bar(
    parent_sales.sort_values(by = 'Dollars',ascending=False)[:15],
    x='Parent Customer',
    y='Dollars',
    # color='Segment Description 2',
    title='<b>Sales by Parent</b>',
    template = 'plotly_white',
    labels={'Parent Customer':'',
            'Dollars':'<b>$USD</b>'}
)
# ---- CREATE TWO MORE COLUMNS AND PLACE GRAPHS ----
left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_parent_sales, theme = 'streamlit', use_container_width=True)
right_column.plotly_chart(fig_dist_sales, theme = 'streamlit', use_container_width=True)




# ---- REMOVE UNWANTED STREAMLIT STYLING ----
hide_st_style = """
            <style>
            Main Menu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
            
st.markdown(hide_st_style, unsafe_allow_html=True)