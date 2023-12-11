import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='Dot Sales',
                   page_icon=":bar_chart:",
                   layout='wide'
)


# ---- PULL IN DATA ----
@st.cache
def get_data_from_excel():
    df = pd.read_excel(
        io='data.xlsx',
        engine='openpyxl',
        sheet_name='dot_sales',
        skiprows=0,
        usecols='A:AH',
        nrows=16659
    )
    return df

df = get_data_from_excel()

# ---- CREATE FILTERS AND SIDEBAR
# st.sidebar.header('Filter Here:')
year = st.sidebar.multiselect(
    "Year:",
    options=df['Invoice Date'].dt.year.unique(),
    default=df['Invoice Date'].dt.year.unique(),
)

# st.sidebar.header('Filter Here:')
segment = st.sidebar.multiselect(
    "Market Segment:",
    options=df['Segment Description 2'].unique(),
    default=df['Segment Description 2'].unique(),
)


# QUERY THE DATEFRAME BASED ON FILTER SELECTIONS
df_selection = df[
    (df['Invoice Date'].dt.year.isin(year)) & (df['Segment Description 2'].isin(segment))
    ][['Table',
       'Invoice Date',
       'Parent Customer',
       'Customer Name',
       'MFG #',
       'Item Full Description',
       'Qty Ordered',
       'Qty Received',
       'Dollars',
       'Segment Description 2']]

st.markdown("raw data")
st.markdown(f"{len(df_selection)} rows")
st.dataframe(df_selection)


# ---- MAINPAGE ----
st.title(":bar_chart: Dot Sales")
st.markdown("##")


# ---- TOP KPI's Row ----
total_sales = int(df_selection['Dollars'].sum())
total_rec = int(df_selection['Qty Received'].sum())
total_ordered = int(df_selection['Qty Ordered'].sum())

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader('Total Sales')
    st.subheader(f"US $ {total_sales:,}")
with middle_column:
    st.subheader('Total Cases Received')
    st.subheader(f"{total_rec:,}")
with right_column:
    st.subheader('Total Cases Ordered')
    st.subheader(F"{total_ordered:,}")

# line divider
st.markdown("---")


# ---- CREATE GRAPHS ----
seg_sales = df_selection.groupby('Segment Description 2',as_index=False)['Dollars'].sum()
fig_seg_sales = px.bar(
    seg_sales.sort_values(by = 'Dollars',ascending=False),
    x='Dollars',
    y='Segment Description 2',
    orientation = 'h',
    title = "<b>Sales by Market Segment</b>",
    template = 'plotly_white',
    color='Segment Description 2',
    labels={'Segment Description 2':'Market Segment',
            'Dollars':'Sales in $USD'},
    # width=800
).update_layout(showlegend=False)

sales_per_day = df_selection.groupby(pd.Grouper(freq='W', key='Invoice Date'))['Dollars'].sum()
fig_sales_per_day = px.line(
    sales_per_day,
    x=sales_per_day.index,
    y='Dollars',
    title='<b>Daily Sales</b>',
    template = 'plotly_white'
)

# ---- SHOW GRAPHS STACKED VERTICALLY ----
st.plotly_chart(fig_sales_per_day, use_container_width=False)
st.plotly_chart(fig_seg_sales,use_container_width=False)

# ---- CREATE TWO COLUMNS AND PLACE GRAPHS ----
# left_column, right_column = st.columns(2)
# left_column.plotly_chart(fig_sales_per_day, use_container_width=True)
# right_column.plotly_chart(fig_seg_sales, use_container_width=True)

# ---- CREATE ROW 2 GRAPHS ----
dist_sales = df_selection.groupby('Customer Name',as_index=False)['Dollars'].sum()
fig_dist_sales = px.bar(
    dist_sales.sort_values(by = 'Dollars',ascending=False)[:20],
    x='Customer Name',
    y='Dollars',
    title='<b>Sales by Distributor</b>',
    height=525,
    template = 'plotly_white'
)

parent_sales = df_selection.groupby(['Parent Customer','Segment Description 2'],as_index=False)['Dollars'].sum()
fig_parent_sales = px.bar(
    parent_sales.sort_values(by = 'Dollars',ascending=False)[:15],
    x='Parent Customer',
    y='Dollars',
    # color='Segment Description 2',
    title='<b>Sales by Parent</b>',
    template = 'plotly_white'
)

# ---- SHOW GRAPHS STACKED VERTICALLY ----
st.plotly_chart(fig_parent_sales, use_container_width=True)
st.plotly_chart(fig_dist_sales, use_container_width=True)

# ---- CREATE TWO COLUMNS AND SHOW GRAPHS HORIZONTALLY ----
# left_column, right_column = st.columns(2)
# left_column.plotly_chart(fig_parent_sales, use_container_width=True)
# right_column.plotly_chart(fig_dist_sales, use_container_width=True)

# ---- REMOVE UNWANTED STREAMLIT STYLING ----
hide_st_style = """
            <style>
            Main Menu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
            
st.markdown(hide_st_style, unsafe_allow_html=True)