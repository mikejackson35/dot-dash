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

year = st.sidebar.selectbox(
    "Year Filter:", all_sales['Invoice Date'].dt.year.unique()
)

# def options_select():
#     if "selected_options" in st.session_state:
#         if -1 in st.session_state["selected_options"]:
#             st.session_state["selected_options"] = available_options[0]
#             st.session_state["max_selections"] = 1
#         else:
#             st.session_state["max_selections"] = len(available_options)

# available_options = [i for i in range(-1,2)]
# if "max_selections" not in st.session_state:
#     st.session_state["max_selections"] = len(available_options)

# st.multiselect(
#     label="Select an Option",
#     options=available_options,
#     key  ="selected_options",
#     max_selections=st.session_state["max_selections"],
#     on_change=options_select,
#     format_func=lambda x: "All" if x == -1 else f"Option {x}",
# )

# st.write(
#     available_options[1:] if st.session_state["max_selections"] == 1
#                           else st.session_state["selected_options"]
# )

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

st.dataframe(table_to_display.round(2))

# ---- MAINPAGE ----
st.markdown("<h1>Awake</h1>", unsafe_allow_html=True)

# ---- TOP KPI's Row ----
total_sales = int(df_selection['Dollars'].sum())
mean_sales = int(df_selection['Dollars'].mean())
customer_count = int(df_selection['Customer'].nunique())

logo, left_column, middle_column, right_column = st.columns([1,1.33,1.33,1.34])
with logo:
    st.image("Nevil.png", width=100)
with left_column:
    st.markdown('<h4>Total Sales</h4>', unsafe_allow_html=True)
    st.markdown(f"<h2>${total_sales:,}</h2>", unsafe_allow_html=True)
with middle_column:
    st.markdown('<h4>$/Customer</h4>', unsafe_allow_html=True)
    st.markdown(f"<h2>${mean_sales:,}</h2>", unsafe_allow_html=True)
with right_column:
    st.markdown('<h4>Num of Customers</h4>', unsafe_allow_html=True)
    st.markdown(F"<h2>{customer_count:,}</h2>", unsafe_allow_html=True)

st.markdown("##")

# METRICS
vending_23 = all_sales[(all_sales['Invoice Date'].dt.year == 2023) & (all_sales[all_sales['Market Segment'] == 'Vending'])].Dollars.sum()
vending_22 = all_sales[(all_sales['Invoice Date'].dt.year == 2022) & (all_sales[all_sales['Market Segment'] == 'Vending'])].Dollars.sum()
yoy_vend = int(vending_23-vending_22)
yoy_vend_perc = round(int(vending_23-vending_22) / vending_22,2)


online_23 = all_sales[(all_sales['Invoice Date'].dt.year == 2023) & (all_sales[all_sales['Market Segment'] == 'Online'])].Dollars.sum()
online_22 = all_sales[(all_sales['Invoice Date'].dt.year == 2022) & (all_sales[all_sales['Market Segment'] == 'Online'])].Dollars.sum()
yoy_online = int(online_23-online_22)
yoy_online_perc = round(int(online_23-online_22) / online_22,2)

alt_23 = all_sales[(all_sales['Invoice Date'].dt.year == 2023) & (all_sales[all_sales['Market Segment'] == 'Alternative Retail'])].Dollars.sum()
alt_22 = all_sales[(all_sales['Invoice Date'].dt.year == 2022) & (all_sales[all_sales['Alternative Retial'] == 'Alternative Retail'])].Dollars.sum()
yoy_alt = int(alt_23-alt_22)
yoy_alt_perc = round(int(alt_23-alt_22) / alt_22,2)

col1, col2, col3 = st.columns(3)
col1.metric(label='Vending', value=yoy_vend, delta = yoy_vend_perc)
col2.metric(label='Online', value=yoy_online, delta = yoy_online_perc)
col3.metric(label='Alternative Retail', value=yoy_alt, delta = yoy_alt_perc)


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
).update_layout(showlegend=False, title_x=0.5)


sales_per_day = df_selection.groupby(pd.Grouper(freq='W', key='Invoice Date'))['Dollars'].sum()
fig_sales_per_day = px.scatter(
    sales_per_day,
    x=sales_per_day.index,
    y='Dollars',
    title='<b>Weekly Sales</b>',
    template = 'plotly_white',
    labels={'Invoice Date':'',
            'Dollars':'<b>$USD</b>'},
    trendline="rolling", trendline_options=dict(function="mean", window=6), trendline_scope="overall",
).update_layout(showlegend=False, title_x=0.5)

fig_sales_per_day.update_layout(showlegend=False)
fig_sales_per_day.show()

# ---- CREATE TWO COLUMNS AND PLACE GRAPHS ----
left_column, right_column = st.columns([3,2])
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
).update_layout(title_x=0.5)

parent_sales = df_selection.groupby(['Parent Customer','Market Segment'],as_index=False)['Dollars'].sum()
fig_parent_sales = px.bar(
    parent_sales.sort_values(by = 'Dollars',ascending=False)[:15],
    x='Parent Customer',
    y='Dollars',
    title='<b>Sales by Parent</b>',
    template = 'plotly_white',
    labels={'Parent Customer':'',
            'Dollars':'<b>$USD</b>'}
).update_layout(showlegend=False, title_x=0.5)

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