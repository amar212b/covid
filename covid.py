#!/usr/bin/env python
# coding: utf-8

# In[27]:


import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly
import dash_table

import pandas as pd
import numpy as np
from datetime import datetime,timedelta

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
# from plotly.offline import iplot, init_notebook_mode
# init_notebook_mode()

import requests
import json

from scipy.interpolate import interp1d

import geopandas as gpd




# In[28]:


state_df = pd.read_csv('https://api.covid19india.org/csv/latest/state_wise.csv')
state_district_df=pd.read_csv('https://api.covid19india.org/csv/latest/district_wise.csv')
state_wise_daily_df=pd.read_csv('https://api.covid19india.org/csv/latest/state_wise_daily.csv')
national_df=pd.read_json('https://api.covid19india.org/v3/data.json')
case_time_series_df=pd.read_csv('https://api.covid19india.org/csv/latest/case_time_series.csv')
country_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_country.csv')
death_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
confirmed_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
recovered_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')

state_df.drop(['State_Notes', 'Delta_Deaths','Delta_Recovered','Delta_Confirmed'], axis=1, inplace=True)

state_df.drop(0,inplace=True)


# In[29]:




state_district_df=state_district_df.loc[:,['State_Code','State','District','Confirmed','Active','Recovered','Deceased']]
state_district_df_disp=state_district_df.loc[:,['State','District','Confirmed','Active','Recovered','Deceased']]

# Time updates
dt = datetime.now()
dt1 = dt + timedelta(hours = 5, minutes = 30)
update = dt.strftime('%B ,%d at %H:%M')
state_df['Last_Updated_Time'] = pd.to_datetime(state_df['Last_Updated_Time'])
max_time=state_df['Last_Updated_Time'].max()
min_time=state_df['Last_Updated_Time'].min()
#world data
country_df['Last_Update'] = pd.to_datetime(country_df['Last_Update'])
max_time_world=country_df['Last_Update'].max()
max_time_world


#World data increase 
df_confirmed_total = confirmed_df.iloc[:, 4:].sum(axis=0)
df_confirmed_total = pd.Series(df_confirmed_total)

df_confirmed_total1 = pd.DataFrame(df_confirmed_total,columns=['Confirmed']) 
df_confirmed_total1.reset_index(level=0, inplace=True)
df_confirmed_total1.rename(columns={'index': 'Date'}, inplace=True)


df_recovered_df_total = recovered_df.iloc[:, 4:].sum(axis=0)
df_recovered_df_total1 = pd.DataFrame(df_recovered_df_total,columns=['Recovered']) 
df_recovered_df_total1.reset_index(level=0, inplace=True)
df_recovered_df_total1.rename(columns={'index': 'Date'}, inplace=True)
df_merge_time_series_world=pd.merge(df_confirmed_total1,df_recovered_df_total1,on='Date')
df_merge_time_series_world

df_death_total = death_df.iloc[:, 4:].sum(axis=0)
df_death_total1 = pd.DataFrame(df_death_total,columns=['Deaths']) 
df_death_total1.reset_index(level=0, inplace=True)
df_death_total1.rename(columns={'index': 'Date'}, inplace=True)

df_merge_time_series_world1=pd.merge(df_merge_time_series_world,df_death_total1,on='Date')



df_merge_time_series_world1['Active']=df_merge_time_series_world1['Confirmed']-df_merge_time_series_world1['Recovered']-df_merge_time_series_world1['Deaths']


df_merge_time_series_world1['recovery_rate_global']=(df_merge_time_series_world1['Recovered']/df_merge_time_series_world1['Confirmed'])*100
df_merge_time_series_world1['death_rate_global']=(df_merge_time_series_world1['Deaths']/df_merge_time_series_world1['Confirmed'])*100

#percentage and number increase of world data
confirmed_growth_global1 = '+' + str (round (((df_merge_time_series_world1.iloc[-1][1] - df_merge_time_series_world1.iloc[-2][1]) / df_merge_time_series_world1.iloc[-2][1] *100 ) , 2)) + '%'
confirmed_growth_global1_num='+' + str(df_merge_time_series_world1.iloc[-1][2] - df_merge_time_series_world1.iloc[-2][2])

confirmed_death_global1 = '+' + str (round (((df_merge_time_series_world1.iloc[-1][3] - df_merge_time_series_world1.iloc[-2][3]) / df_merge_time_series_world1.iloc[-2][3] *100 ) , 2)) + '%'
confirmed_death_global1_num='+' + str(df_merge_time_series_world1.iloc[-1][3] - df_merge_time_series_world1.iloc[-2][3])

confirmed_recovered_global1 = '+' + str (round (((df_merge_time_series_world1.iloc[-1][2] - df_merge_time_series_world1.iloc[-2][2]) / df_merge_time_series_world1.iloc[-2][2] *100 ) , 2)) + '%'
confirmed_recovered_global1_num='+' + str(df_merge_time_series_world1.iloc[-1][2] - df_merge_time_series_world1.iloc[-2][2])

confirmed_active_global1 = '+' + str (round (((df_merge_time_series_world1.iloc[-1][4] - df_merge_time_series_world1.iloc[-2][4]) / df_merge_time_series_world1.iloc[-2][4] *100 ) , 2)) + '%'
confirmed_active_global1_num='+' + str (df_merge_time_series_world1.iloc[-1][4] - df_merge_time_series_world1.iloc[-2][4])

# Getting latest country data
r_latest_stats = requests.get('https://api.rootnet.in/covid19-in/stats/latest')
latest_stats = r_latest_stats.json()
last_refresh=latest_stats['lastRefreshed']

# Statewise history and total cases for each day
r_statewise_history = requests.get('https://api.rootnet.in/covid19-in/unofficial/covid19india.org/statewise/history')
statewise_history = r_statewise_history.json()

# Parsing JSON response for country data
total_summary = latest_stats['data']['summary']
regional_data = latest_stats['data']['regional']
last_referenced = latest_stats['lastRefreshed']
last_referenced_str = str(last_referenced)

states = [eachstate['loc'] for eachstate in regional_data]
confirmed_cases = [confcases['confirmedCasesIndian'] for confcases in regional_data]
discharged = [discharg['discharged'] for discharg in regional_data]
deaths = [deaths['deaths'] for deaths in regional_data]
foreign_cases = [foreign_cases['confirmedCasesForeign'] for foreign_cases in regional_data]
all_regional_data = list(zip(states,confirmed_cases,discharged,deaths,foreign_cases))



state_df_1=state_df[state_df.State != 'State Unassigned']

state_df.sort_values('Confirmed', ascending=False, inplace=True)

country_df.drop(['People_Tested', 'People_Hospitalized'], axis=1, inplace=True)
country_df.rename(columns={'Country_Region': 'Country', 'Long_': 'Long'}, inplace=True)
# sorting country_df with highest confirm case

country_df.sort_values('Confirmed', ascending=False, inplace=True)


state_wise_daily_df_confirmed = state_wise_daily_df[state_wise_daily_df['Status']=='Confirmed']
df_type_confirmed = pd.melt(state_wise_daily_df_confirmed.copy(deep=True), id_vars=["Date","Status"], var_name='State_Code', value_name='Value')
df_type_confirmed = pd.merge(df_type_confirmed,state_district_df,on='State_Code', how='inner')
df_type_confirmed = df_type_confirmed.loc[:, ['Date', 'Status','State_Code','State','Value']]
# dropping ALL duplicte values 
df_type_confirmed=df_type_confirmed.drop_duplicates()
df_type_confirmed=df_type_confirmed[df_type_confirmed.State != 'State Unassigned']

state_wise_daily_df_Recovered = state_wise_daily_df[state_wise_daily_df['Status']=='Recovered']
df_type_Recovered = pd.melt(state_wise_daily_df_Recovered.copy(deep=True), id_vars=["Date","Status"], var_name='State_Code', value_name='Value')
df_type_Recovered = pd.merge(df_type_Recovered,state_district_df,on='State_Code', how='inner')
df_type_Recovered = df_type_Recovered.loc[:, ['Date', 'Status','State_Code','State','Value']]
# dropping ALL duplicte values 
df_type_Recovered=df_type_Recovered.drop_duplicates()
df_type_Recovered=df_type_Recovered[df_type_Recovered.State != 'State Unassigned']

state_wise_daily_df_Deceased = state_wise_daily_df[state_wise_daily_df['Status']=='Deceased']
df_type_Deceased = pd.melt(state_wise_daily_df_Deceased.copy(deep=True), id_vars=["Date","Status"], var_name='State_Code', value_name='Value')
df_type_Deceased = pd.merge(df_type_Deceased,state_district_df,on='State_Code', how='inner')
df_type_Deceased = df_type_Deceased.loc[:, ['Date', 'Status','State_Code','State','Value']]
# dropping ALL duplicte values 
df_type_Deceased=df_type_Deceased.drop_duplicates()
df_type_Deceased=df_type_Deceased[df_type_Deceased.State != 'State Unassigned']

state_wise_daily_df_Active = state_wise_daily_df[state_wise_daily_df['Status']=='Active']
df_type_Active = pd.melt(state_wise_daily_df_Active.copy(deep=True), id_vars=["Date","Status"], var_name='State_Code', value_name='Value')
df_type_Active = pd.merge(df_type_Active,state_district_df,on='State_Code', how='inner')
df_type_Active = df_type_Active.loc[:, ['Date', 'Status','State_Code','State','Value']]
# dropping ALL duplicte values 
df_type_Active=df_type_Active.drop_duplicates()

# Creating a pandas data frame for india data
df_latest_stats = pd.DataFrame(all_regional_data, columns = ['State', 'Confirmed cases', 'Discharged','Deaths','Foreign cases'])
df_latest_stats['Active Cases'] = df_latest_stats['Confirmed cases']-df_latest_stats['Discharged']
df_latest_stats['% Death'] = (df_latest_stats['Deaths'] / df_latest_stats['Confirmed cases']) * 100
df_latest_stats


state_df_latest_stats = pd.DataFrame(state_df_1, columns = ['State', 'Confirmed', 'Recovered','Deaths','Active'])

#india time series data
case_time_series_df['Active Cases'] = case_time_series_df['Total Confirmed']-case_time_series_df['Total Recovered']-case_time_series_df['Total Deceased']
df1 = case_time_series_df.copy()
cols = ['Total Confirmed', 'Total Recovered', 'Total Deceased','Active Cases']
df1[cols] = df1[cols].apply(pd.to_numeric, errors='coerce')
df1[cols]
confirmed_growth = '+' + str (round (((df1.iloc[-1][2] - df1.iloc[-2][2]) / df1.iloc[-2][2] *100 ) , 2)) + '%'
recovered_growth = '+' + str (round (((df1.iloc[-1][4] - df1.iloc[-2][4]) / df1.iloc[-2][4] *100 ) , 2)) + '%'
death_growth = '+' + str (round (((df1.iloc[-1][6] - df1.iloc[-2][6]) / df1.iloc[-2][6] *100 ) , 2) ) + '%'
active_growth= '+' + str (round (((df1.iloc[-1][7] - df1.iloc[-2][7]) / df1.iloc[-2][7] *100 ) , 2) ) + '%'

confirmed_num_increase= '+' + str(df1.iloc[-1][2] - df1.iloc[-2][2])
confirmed_num_increase
recovered_num_increase= '+' + str(df1.iloc[-1][4] - df1.iloc[-2][4])
recovered_num_increase
death_num_increase= '+' + str(df1.iloc[-1][6] - df1.iloc[-2][6])
death_num_increase
active_num_increase='+' + str(df1.iloc[-1][7] - df1.iloc[-2][7])
active_num_increase


case_time_series_df['recover_rate_india']=(case_time_series_df['Total Recovered']/case_time_series_df['Total Confirmed'])*100
case_time_series_df['death_rate_india']=(case_time_series_df['Total Deceased']/case_time_series_df['Total Confirmed'])*100


# In[30]:


# # reading the shape file of map of India in GeoDataFrame
# map_data = gpd.read_file(r"C:\corona\corona-app1\Igismap\Indian_States.shp")
# map_data.rename(columns = {'st_nm':'States/UT'}, inplace = True)
# map_data
# map_data['States/UT'] = map_data['States/UT'].str.replace('&','and')
# map_data['States/UT'].replace('Arunanchal Pradesh',
                              # 'Arunachal Pradesh', inplace = True)
# map_data['States/UT'].replace('Telangana', 
                              # 'Telengana', inplace = True)
# map_data['States/UT'].replace('NCT of Delhi', 
                              # 'Delhi', inplace = True)
# map_data['States/UT'].replace('Andaman and Nicobar Island', 
                              # 'Andaman and Nicobar Islands', 
                               # inplace = True)

# map_data.rename(columns={'States/UT': 'State', 'Long_': 'Long'}, inplace=True)


# # In[31]:


# # Generate centroids for each polygon to use as marker locations
# map_data['lon_lat'] = map_data['geometry'].apply(lambda row: row.centroid)
# map_data['LON'] = map_data['lon_lat'].apply(lambda row: row.x)
# map_data['LAT'] = map_data['lon_lat'].apply(lambda row: row.y)
# map_data = map_data.drop('lon_lat', axis=1)

# lon = map_data['LON'][0]
# lat = map_data['LAT'][0]


# # In[32]:


# merged_data = pd.merge(map_data, state_df, 
                       # how = 'inner', on = 'State')


# # In[33]:


# # India map heading
# margin = merged_data['Confirmed'].values.tolist()
# circel_range = interp1d([0, max(margin)], [0,12])
# circle_radius = circel_range(margin)

# global_map_heading = html.H2(children='India map view', className='mt-5 py-4 pb-3 text-center')

# # ploting the map
# map_fig = px.scatter_mapbox(merged_data, lat="LAT", lon="LON", hover_name="State", hover_data=["Confirmed", "Deaths"],
                        # color_discrete_sequence=["#e60039"], zoom=3.5, height=500, size_max=70, size=circle_radius)

# map_fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0}, height=520)


# In[35]:





""" margin = country_df['Confirmed'].values.tolist()
circel_range = interp1d([1, max(margin)], [0.2,12])
circle_radius = circel_range(margin)
# ploting world map
# fixing the size of circle

margin = country_df['Confirmed'].values.tolist()
circel_range = interp1d([1, max(margin)], [0.2,12])
circle_radius = circel_range(margin) """

##chrolopeth map
fig_chloropeth = go.Figure(data=go.Choropleth(
    locations = country_df['ISO3'],
    z = country_df['Confirmed'],
    text = country_df['Country'],
    colorscale = 'Blues',
    autocolorscale=False,
    locationmode='ISO-3',
    reversescale=True,
    marker_line_color='darkgray',
    marker_line_width=0.5,
    colorbar_tickprefix = '$',
    colorbar_title = 'Confirmed<br>Cases',
))

fig_chloropeth.update_layout(
    title_text='2019 CoronaVirus',
    title={
        'text': "2019 CoronaVirus World View",
        'y':0.96,
        'x':0.4,
        'xanchor': 'center',
        'yanchor': 'top'},
    geo=dict(
        showframe=False,
        showcoastlines=False,
        projection_type='equirectangular'
    ),
  
)

#app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.CYBORG])
app.title = 'Covid19 - Dashboard'
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#Overwrite your CSS setting by including style locally
colors = {
    'background': '#1b3942',#5bc0de',
    'text': '#d9534f',
    'figure_text': '#ffffff',
    'confirmed_text':'#3CA4FF',
    'deaths_text':'#f44336',
    'recovered_text':'#5A9E6F',
    'highest_case_bg':'#393939',
    
}

colors1 = {
    'background': '#111111',
    'text': '#7FDBFF'
}

#COLOR SCHEME
colors2 = {
    'background': '#111111',
    'text': '#BEBEBE',
    'grid': '#333333'
}
# navbar code
navbar = dbc.NavbarSimple(
    children=[

        dbc.NavItem(html.A("India Data", href="#nav-India-data1", style = {'color': '#fff'}), className="mr-5"),
        dbc.NavItem(html.A("State Data", href="#nav-daily-graph", style = {'color': '#fff'}), className="mr-5"),
        
        dbc.NavItem(html.A("State-District Data", href="#nav-cr-link", style = {'color': '#fff'}), className="mr-5"),
    ],
    brand="COVID-19 Dashboard",
    brand_href="/",
    color="dark",
    dark=True,
    className="p-3 fixed-top"
)

# main heading

main_heading = dbc.Container(
[
    html.H1(["COVID-19 Dashboard Summary"], className="my-5 pt-5 text-center"),
 ]
, className='pt-3')

# what is covid-19

what_is_covid = dbc.Container(
    [
        html.Div([
            html.H3(''),
            html.P("Refresh browser for latest updates...."),
            html.A(html.Button('Refresh Data'),href='/'),
            html.P("Last Application updated on:  " + update + ""),
            html.P("Last World Data Refreshed on:  " + str(max_time_world) + ""),
            html.P("Last India Data Refreshed on:" + str(max_time) + "")
           
        ])
    ]
, className="mb-5") 




world_tally = dbc.Container(
    [
        html.H2('Global Data', style = {'text-align': 'center'}),
        
        dbc.Row(
            [
                dbc.Col(children = [html.H4('Confirmed',style = {'color': 'black'}), html.P(style={'color': 'grey',  'fontSize': 20,'height': '5px'},
                                                                          children=confirmed_growth_global1_num + '(' + confirmed_growth_global1 + ')' ),
                        html.Div(country_df['Confirmed'].sum(), className='text-info', style = {'font-size': '34px', 'font-weight': '700'})],
                        width=3, className='text-center bg-light border-right p-3', style = {'border-top-left-radius': '6px', 'border-bottom-left-radius': '6px'}),
                
                dbc.Col(children = [html.H4('Recovered', style = {'padding-top': '0px','color': 'black'}),html.P(style={'color': 'grey',  'fontSize': 20,'height': '5px'},
                                                                          children=confirmed_recovered_global1_num + '(' + confirmed_recovered_global1 + ')' ),
                        html.Div(country_df['Recovered'].sum(), className='text-success', style = {'font-size': '34px', 'font-weight': '700'})],
                        width=3, className='text-center bg-light border-right p-3'),
                
                dbc.Col(children = [html.H4('Deaths', style = {'padding-top': '0px','color': 'black'}), html.P(style={'color': 'grey',  'fontSize': 20,'height': '5px'},
                                                                          children=confirmed_death_global1_num + '(' + confirmed_death_global1 + ')' ),
                        html.Div(country_df['Deaths'].sum(), className='text-danger', style = {'font-size': '34px', 'font-weight': '700'})],
                        width=3, className='text-center bg-light border-right p-3'),
                
                dbc.Col(children = [html.H4('Active',style = {'color': 'black'}),html.P(style={'color': 'grey',  'fontSize': 20,'height': '5px'},
                                                                          children=confirmed_active_global1_num + '(' + confirmed_active_global1 + ')' ),
                        html.Div(country_df['Active'].sum(),className='text-warning', style = {'font-size': '34px', 'font-weight': '700'})],
                        width=3, className='text-center bg-light p-3', style = {'border-top-right-radius': '6px', 'border-bottom-right-radius': '6px'}),
            ]
        , className='my-5 shadow justify-content-center'),
            
    ]
)


# Create subplots: use 'domain' type for Pie subplot
fig_pie = make_subplots(rows=2, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}],[{'type':'domain'},{'type':'domain'}]],
                    subplot_titles=['Confirmed', 'Active','Recovered','Death'])
fig_pie.add_trace(go.Pie(labels=state_df_1['State'], values=state_df_1['Confirmed'], name="Confirmed"),
              1, 1)
fig_pie.add_trace(go.Pie(labels=state_df_1['State'], values=state_df_1['Active'], name="Active"),
              1, 2)
fig_pie.add_trace(go.Pie(labels=state_df_1['State'], values=state_df_1['Recovered'], name="Recovered"),
              2, 1)
fig_pie.add_trace(go.Pie(labels=state_df_1['State'], values=state_df_1['Deaths'], name="Deaths"),
              2, 2)
# Use `hole` to create a donut-like pie chart
fig_pie.update_traces(textposition='inside')
fig_pie.update_layout(font=dict(color='white'),
    title_text="Corona State Wise",
    title={
        'text': "Corona State Wise Percentage India",
        'y':0.96,
        'x':0.4,
        'xanchor': 'center',
        'yanchor': 'top'},
    height=850,width=930,paper_bgcolor=colors['background'],
    plot_bgcolor=colors['background'])

# select, state, no of days and category

state_tally = dbc.Container(
    [
        html.H2(id='nav-India-data1',children='India Data', style = {'text-align': 'center'}),
        
        dbc.Row(
            [
                dbc.Col(children = [html.H4('Confirmed',style = {'color': 'black'}), html.P(style={'color': 'grey',  'fontSize': 20,'height': '5px'},
                                                                          children=confirmed_num_increase + '(' + confirmed_growth + ')' ),
                        html.Div(state_df['Confirmed'].sum(), className='text-info', style = {'font-size': '34px', 'font-weight': '700'})],
                        width=3, className='text-center bg-light border-right p-2', style = {'border-top-left-radius': '6px', 'border-bottom-left-radius': '6px'}),
                        

                dbc.Col(children = [html.H4('Recovered',style = {'padding-top': '0px','color': 'black'}),html.P(style={'color': 'grey',  'fontSize': 20,'height': '5px'},
                                                                          children=recovered_num_increase + '(' + recovered_growth + ')'),
                        html.Div(state_df['Recovered'].sum(), className='text-success', style = {'font-size': '34px', 'font-weight': '700'})],
                        width=3, className='text-center bg-light border-right p-2'),
                
                dbc.Col(children = [html.H4('Deaths',style = {'padding-top': '0px','color': 'black'}), html.P(style={'color': 'grey',  'fontSize': 20,'height': '5px'},
                                                                          children=death_num_increase + '(' + death_growth + ')'),
                        html.Div(state_df['Deaths'].sum(), className='text-danger', style = {'font-size': '34px', 'font-weight': '700'})],
                        width=3, className='text-center bg-light border-right p-2'),
                
                dbc.Col(children = [html.H4('Active',style = {'color': 'black'}),html.P(style={'color': 'grey',  'fontSize': 20,'height': '5px'},
                                                                          children=active_num_increase + '(' + active_growth + ')'),
                        html.Div(state_df['Active'].sum()+state_df['Migrated_Other'].sum(),className='text-warning', style = {'font-size': '34px', 'font-weight': '700'})],
                        width=3, className='text-center bg-light p-2', style = {'border-top-right-radius': '6px', 'border-bottom-right-radius': '6px'}),
            ]
        , className='my-4 shadow justify-content-center'),
            
    ]
)

global_map_heading = html.H2(children='World map view', className='mt-5 py-4 pb-3 text-center')

# # ploting the map
# map_fig = px.scatter_mapbox(country_df, lat="Lat", lon="Long", hover_name="Country", hover_data=["Confirmed", "Deaths"],
#                         color_discrete_sequence=["#e60039"], zoom=2, height=500, size_max=50, size=circle_radius)

# map_fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0}, height=520)


# State wise

daily_graph_heading = html.H2(id='nav-daily-graph', children='COVID-19 Total State Wise Cases ', className='mt-5 pb-3 text-center',style={
            'textAlign': 'center',
            'color': 'white'
        })
daily_graph_heading1 = html.H4(children='State Wise Case Summary ', className='mt-5 pb-3 text-center',style={
            'textAlign': 'center',
            'color': 'black'
        })

daily_graph_heading2 = html.H4(children='State - District Wise Case Summary ', className='mt-5 pb-3 text-center',style={
            'textAlign': 'center',
            'color': 'white'
        })       

# dropdown to select the state, category and number of days

daily_state = state_df_1['State'].unique().tolist()
daily_state_list = []

my_df_type = ['Confirmed cases', 'Recovered cases','Deceased']
my_df_type_list = []

for i in daily_state:
    daily_state_list.append({'label': i, 'value': i})
    
for i in my_df_type:
    my_df_type_list.append({'label': i, 'value': i})
    
# dropdown to select state
state_dropdown = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(children = [html.Label('Select State'), 
                        html.Div(dcc.Dropdown(id = 'select-state', options = daily_state_list, value='Uttar Pradesh',clearable=False,style= {'color':'black'}))],
                        width=3, className='p-2 mr-5'),
                
                dbc.Col(children = [html.Label('Drag to choose no of Days', style = {'padding-top': '0px'}),
                        html.Div(dcc.Slider( id = 'select-date',
                                            min=5,
                                            max=len(df_type_confirmed['Date'].iloc[:]),
                                            step=1,
                                            value=40
                                        ,className='p-0'), className='mt-3')],
                        width=3, className='p-2 mx-5'),
                
                dbc.Col(children = [html.Label('Select category', style = {'padding-top': '0px'}), 
                        html.Div(dcc.Dropdown(id = 'select-category', options = my_df_type_list, value='Confirmed cases',clearable=False,style= {'color':'black'}))],
                        width=3, className='p-2 ml-5'),
            ]
        , className='my-4 justify-content-center'),
            
    ]
)




# heading 
# cr_heading = html.H2(id='nav-cr-link', children='Confirmed and Recovered cases', className='mt-5 pb-3 text-center')

# confrirm and recovered cases top 10 states
top_state = state_df.head(10)
top_state_name = list(top_state['State'].values)

cr = go.Figure(data=[
    go.Bar(name='Confirmed',marker_color='#468499', x=top_state_name, y=list(top_state['Confirmed'])),
    go.Scatter(name='Recovered', marker_color='#1abc9c',x=top_state_name, y=list(top_state['Recovered'])),
    go.Scatter(name='Active', marker_color='#ffd700',x=top_state_name, y=list(top_state['Active'])),
])

# Change the bar mode
cr.update_layout(barmode='group', height=500, 
        title_text="Top 10 states with Confirmed and Recovered case",
        title={
        'text': "Top 10 states with Case in India",
        'y':0.96,
        'x':0.4,
        'xanchor': 'center',
        'yanchor': 'top'},
        yaxis={'title': 'Cases','fixedrange':True},
        paper_bgcolor=colors['background'],
        plot_bgcolor=colors['background'],
        font=dict(color='white')
        )


# confrirm and recovered cases top 10 countries
top_country = country_df.head(10)
top_country_name = list(top_country['Country'].values)


cr1 = go.Figure(data=[
    go.Bar(name='Confirmed',marker_color='#468499', x=top_country_name, y=list(top_country['Confirmed'])),
    go.Scatter(name='Recovered', marker_color='#1abc9c',x=top_country_name, y=list(top_country['Recovered'])),
    go.Scatter(name='Active', marker_color='#ffd700',x=top_country_name, y=list(top_country['Active'])),
])

# Change the bar mode
cr1.update_layout(barmode='group', height=600, 
        title_text="Top 10 countries with Confirmed and Recovered case",
        title={
        'text': "Top 10 countries with Case in World",
        'y':0.96,
        'x':0.4,
        'xanchor': 'center',
        'yanchor': 'top'},
        yaxis={'title': 'Cases','fixedrange':True},
        paper_bgcolor=colors['background'],
        plot_bgcolor=colors['background'],
        font=dict(color='white')
        )

#PLOTS DEFINED HERE
#world data linear plot
fig_world = go.Figure()
fig_world.add_trace(go.Scatter(x=df_merge_time_series_world1['Date'], y=df_merge_time_series_world1['Confirmed'].iloc[:],
                                mode='lines',
                                line_shape = 'linear',
                                name='Confirmed',
                                line=dict(color='#3372FF', width=2),
                                fill='tozeroy', 
                              
                               
                        )),

fig_world.add_trace(go.Scatter(x=df_merge_time_series_world1['Date'], y=df_merge_time_series_world1['Recovered'].iloc[:],
                                mode='lines+markers',
                                line_shape = 'linear',
                                name='Recovered',
                                line=dict(color='#66cd00', width=2),
                                fill='tozeroy', 
                                
                         
                                
                        ))
fig_world.add_trace(go.Scatter(x=df_merge_time_series_world1['Date'], y=df_merge_time_series_world1['Active'].iloc[:],
                                mode='lines+markers',
                                name='Active',
                                line_shape = 'linear',
                                line=dict(color='#ffd700', width=2),
                                fill='tozeroy',
                               
                                
                        ))

fig_world.add_trace(go.Scatter(x=df_merge_time_series_world1['Date'], y=df_merge_time_series_world1['Deaths'].iloc[:],
                                mode='lines+markers',
                                name='Deaths',
                                line_shape = 'linear',
                                line=dict(color='#FF3333', width=2),
                                fill='tozeroy', 
                               
                                
                        ))


fig_world.update_layout(
        title='Cases Across World - Confirmed ,Recovered,Deceased and Active',
        yaxis={'title': 'Cases','fixedrange':True},
        hovermode='x',
        font=dict(
            family="Courier New, monospace",
            size=14,
            color='white',
        ),
        legend=dict(
            traceorder="normal",
            font=dict(
                family="sans-serif",
                size=12,
                color='white'
            ),
            bgcolor=colors['background'],
            borderwidth=5
        ),
        paper_bgcolor=colors['background'],
        plot_bgcolor=colors['background'],
        margin=dict(l=0, r=0, t=65, b=0),
        height=500,

    )

fig_recover_death_world = go.Figure()
fig_recover_death_world.add_trace(go.Scatter(x=df_merge_time_series_world1['Date'], y=df_merge_time_series_world1['recovery_rate_global'].iloc[:],
                                mode='lines',
                                line_shape = 'linear',
                                name='recovery_rate',
                                line=dict(color='#3372FF', width=2),
                                
                              
                               
                        )),

fig_recover_death_world.add_trace(go.Scatter(x=df_merge_time_series_world1['Date'], y=df_merge_time_series_world1['death_rate_global'].iloc[:],
                                mode='lines+markers',
                                line_shape = 'linear',
                                name='death_rate',
                                line=dict(color='#66cd00', width=2),
                                
                                
                         
                                
                        ))

fig_recover_death_world.update_layout(
        # title='Recovery Rate vs Death Rate World',
        title={
        'text': "Recovery Rate vs Death Rate World",
        'y':0.96,
        'x':0.4,
        'xanchor': 'center',
        'yanchor': 'top'},
        hovermode='x',
        font=dict(
            family="Courier New, monospace",
            size=14,
            color="#ffffff",
        ),
        legend=dict(
            traceorder="normal",
            font=dict(
                family="sans-serif",
                size=12,
                color=colors['figure_text']
            ),
            bgcolor=colors['background'],
            borderwidth=5
        ),
        paper_bgcolor=colors['background'],
        plot_bgcolor=colors['background'],
        margin=dict(l=0, r=0, t=65, b=0),
        height=500,
        yaxis={'title': 'Percent','fixedrange':True}
    )

#Graph for daily rise of cases in india
fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=case_time_series_df['Date'], y=case_time_series_df['Total Confirmed'].iloc[:],
                                mode='lines',
                                line_shape = 'linear',
                                name='Confirmed',
                                line=dict(color='#3372FF', width=2),
                                fill='tozeroy', 
                              
                               
                        )),

fig1.add_trace(go.Scatter(x=case_time_series_df['Date'], y=case_time_series_df['Total Recovered'].iloc[:],
                                mode='lines+markers',
                                line_shape = 'linear',
                                name='Recovered',
                                line=dict(color='#66cd00', width=2),
                                fill='tozeroy', 
                                
                         
                                
                        ))
fig1.add_trace(go.Scatter(x=case_time_series_df['Date'], y=case_time_series_df['Active Cases'].iloc[:],
                                mode='lines+markers',
                                name='Active',
                                line_shape = 'linear',
                                line=dict(color='#ffd700', width=2),
                                fill='tozeroy',
                               
                                
                        ))

fig1.add_trace(go.Scatter(x=case_time_series_df['Date'], y=case_time_series_df['Total Deceased'].iloc[:],
                                mode='lines+markers',
                                name='Deaths',
                                line_shape = 'linear',
                                line=dict(color='#FF3333', width=2),
                                fill='tozeroy', 
                               
                                
                        ))


fig1.update_layout(
        title='Cases Across India - Confirmed ,Recovered,Deceased and Active',
        yaxis={'title': 'Cases','fixedrange':True},
        hovermode='x',
        font=dict(
            family="Courier New, monospace",
            size=14,
            color='white',
        ),
        legend=dict(
            traceorder="normal",
            font=dict(
                family="sans-serif",
                size=12,
                color='white'
            ),
            bgcolor=colors['background'],
            borderwidth=5
        ),
        paper_bgcolor=colors['background'],
        plot_bgcolor=colors['background'],
        margin=dict(l=0, r=0, t=65, b=0),
        height=500,

    )




# NEW CASES, PLOT  1
fig_newcases = go.Figure()
fig_newcases.add_trace(go.Scatter(
    x= case_time_series_df['Date'],
    y= case_time_series_df['Daily Confirmed'],
    line_shape = 'spline',
    text = case_time_series_df['Daily Confirmed'].pct_change()*100,
    fill='tozeroy',
    mode='lines+markers',
    marker=dict(size=4, color='#4E62FF',line=dict(width=1, color='#4E62FF')),
    line_color='rgba(55,5,255,0.6)',
    hovertemplate = "New cases as on %{x}<br><b>Growth: %{text}</b><br>Count: %{y}" ,
    showlegend=False,
    name='New Cases')
)
fig_newcases.update_layout(
    title={
        'text': "Daily Confirmed Cases Across India - Percentage",
        'y':0.96,
        'x':0.4,
        'xanchor': 'center',
        'yanchor': 'top'},
    xaxis={'title': 'Timeline','fixedrange':True},
    yaxis={'title': 'New Confirmed Cases','fixedrange':True},
    font=dict(color='white'),
    paper_bgcolor=colors['background'],
    plot_bgcolor=colors['background'],
    height = 500,
    hovermode='closest',
    showlegend=True,

)    

#Bar Graph
fig_newcases_bar = go.Figure()
fig_newcases_bar.add_trace(go.Bar(
    name='Confirmed',
    marker_color='#4E62FF',
    x=case_time_series_df['Date'], 
    y=case_time_series_df['Daily Confirmed']),
),
fig_newcases_bar.update_layout(
    title={
        'text': "Daily Confirmed Cases Across India - Bar",
        'y':0.96,
        'x':0.4,
        'xanchor': 'center',
        'yanchor': 'top'},
    xaxis={'title': 'Timeline','fixedrange':True},
    yaxis={'title': 'New Confirmed Cases','fixedrange':True},
    font=dict(color='white'),
    paper_bgcolor=colors['background'],
    plot_bgcolor=colors['background'],
    height = 500,
    hovermode='closest',
    showlegend=True,

)



fig_recover_death_india = go.Figure()
fig_recover_death_india.add_trace(go.Scatter(x=case_time_series_df['Date'], y=case_time_series_df['recover_rate_india'].iloc[:],
                                mode='lines',
                                line_shape = 'linear',
                                name='recovery_rate',
                                line=dict(color='#3372FF', width=2),
                                
                              
                               
                        )),

fig_recover_death_india.add_trace(go.Scatter(x=case_time_series_df['Date'], y=case_time_series_df['death_rate_india'].iloc[:],
                                mode='lines+markers',
                                line_shape = 'linear',
                                name='death_rate',
                                line=dict(color='#66cd00', width=2),
                                
                                
                         
                                
                        ))




fig_recover_death_india.update_layout(
        # title='Recovery Rate vs Death Rate India',
        title={
        'text': "Recovery Rate vs Death Rate India",
        'y':0.96,
        'x':0.4,
        'xanchor': 'center',
        'yanchor': 'top'},
        hovermode='x',
        font=dict(
            family="Courier New, monospace",
            size=14,
            color="#ffffff",
        ),
        legend=dict(
            traceorder="normal",
            font=dict(
                family="sans-serif",
                size=12,
                color=colors['figure_text']
            ),
            bgcolor=colors['background'],
            borderwidth=5
        ),
        paper_bgcolor=colors['background'],
        plot_bgcolor=colors['background'],
        margin=dict(l=0, r=0, t=65, b=0),
        height=500,
        yaxis={'title': 'Percent','fixedrange':True}
    )


fig = go.Figure(data=[go.Table(
    header=dict(values=list(state_df_latest_stats.columns),
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[state_df_latest_stats.State, state_df_latest_stats.Confirmed, state_df_latest_stats.Recovered,state_df_latest_stats.Deaths,state_df_latest_stats.Active],
               fill_color='lavender',
               align='left'))
])
# create graph for daily report

def state_daily_graph(state, category):
    daily_data = []
    daily_data.append(go.Scatter(
                  x=state['Date'], y=state['Value'], name="Covid-19 daily Trend for states", line=dict(color='#f36')))
    
    # layout=dict(title=dict(text="A Figure Specified By A Graph Object"))
    layout = {
        'title' :'Daily ' + category +'  in ' + state['State'].values[0],
        'title_font_size': 26,
        'height':450,
        'backgroundColor':colors['background'],
        'style': {'backgroundColor': '#1b3942','color':'white'},
        'gridcolor':'black',
        'bgcolor':dict(color='black'),
        'xaxis' : dict(
            title='Date',
            titlefont=dict(
            family='Courier New, monospace',
            size=24,
            color=colors['background'],
        )),
        'yaxis' : dict(
            title='Covid-19 cases',
            titlefont=dict(
            family='Courier New, monospace',
            size=20,
            color=colors['background'],
        )),
        
        }  
    
    figure = {
        'data': daily_data,
        'layout': layout
    }
    
    return figure




# main layout for Dash

app.layout = html.Div(style= {'backgroundColor': '#1b3942','color':'white'},#e5e6eb' },
     children=[
     main_heading,
     what_is_covid,
     world_tally,global_map_heading,
      # global map        
     html.Div(style = { 'width': '96%', 'height': '200%','backgroundColor':colors['background'],
                                'display': 'inline-block',
                                'marginRight': '1.8%', 'verticalAlign': 'top', 'marginTop': '0%',  'marginLeft': '1.8%','marginBottom': '1.8%'},
                children = [
                    dcc.Graph(
                        id='global_graph',
                        figure=fig_chloropeth
                        )
                ]
      ),
      
      html.Br(),
     html.Div(style = { 'width': '96%', 'height': '200%','backgroundColor':colors['background'],
                                'display': 'inline-block',
                                'marginRight': '1.8%', 'verticalAlign': 'top', 'marginTop': '0%',  'marginLeft': '1.8%','marginBottom': '1.8%'},
                children=[dcc.Graph(figure=fig_world,id='world_linear_graph')
                ]),
      html.Br(),
      dcc.Graph(
          id='death_recover_world',
          figure=fig_recover_death_world
      ),
      html.Br(),

       dcc.Graph(
             id='cr1',
             figure=cr1
         )  ,
         html.Br(),
         html.Div(id='nav-India-data',children=[
                state_tally
         ])        
             ,
         html.Br(),
        html.Div(style = { 'width': '96%', 'height': '200%','backgroundColor':colors['background'],
                                'display': 'inline-block',
                                'marginRight': '1.8%', 'verticalAlign': 'top', 'marginTop': '0%',  'marginLeft': '1.8%','marginBottom': '1.8%'},
         children=[dcc.Graph(figure=map_fig,id='india_map_open')
                ]),   
        
         html.Br(),
              
         
     html.Div(style = { 'width': '96%', 'height': '200%','backgroundColor':colors['background'],
                                'display': 'inline-block',
                                'marginRight': '1.8%', 'verticalAlign': 'top', 'marginTop': '0%',  'marginLeft': '1.8%','marginBottom': '1.8%'},
                children=[dcc.Graph(figure=fig1,id='india_graph')
                ]),
     html.Div(
        id = "fresh_pane",
        children =
        [
            html.H2(children='DAY-WISE RISE IN CONFIRMED CASES',
                style={
                    'textAlign': 'center',
                    'color': 'white',
                    'marginTop': '7%'
                    }
                ), 
            html.Div(
                style = { 'width': '96%', 'height': '200%','backgroundColor':colors['background'],
                                'display': 'inline-block',
                                'marginRight': '1.8%', 'verticalAlign': 'top', 'marginTop': '0%',  'marginLeft': '1.8%','marginBottom': '1.8%'},
                children = [
                    html.Div(
                    dcc.Graph(id = 'new_cases', figure = fig_newcases)
                    ),
                   

               ]),  
           
            html.Div(
                    style = { 'width': '96%', 'height': '200%','backgroundColor':colors['background'],
                                'display': 'inline-block',
                                'marginRight': '1.8%', 'verticalAlign': 'top', 'marginTop': '0%',  'marginLeft': '1.8%','marginBottom': '1.8%'},
                    children = [
                    html.Div(
                
                        dcc.Graph(id = 'new_cases_bar', figure = fig_newcases_bar)
                      ),
                    ]),
                    html.Br(),
                    dcc.Graph(id='death_recover_india',
                    figure=fig_recover_death_india),
            ]),   
                                   
    
        
       # state wise graph
      dbc.Container([daily_graph_heading,
                    html.Div(
                        children=[
                            dash_table.DataTable(
                            id="Table",
                            columns=[{"name":i, "id": i} for i in state_df_latest_stats.columns],
                            fixed_rows={'headers': True, 'data': 0},
                            style_header={
                                'backgroundColor': 'rgb(30, 30, 30)',
                                'fontWeight': 'bold'
                            },
                            style_cell={
                                'backgroundColor': 'rgb(100, 100, 100)',
                                'color': '#ffffff',
                                'maxWidth': 0,
                                'fontSize':14,
                                'textAlign': 'center'
                            },
                            style_table={
                                'maxHeight': '350px',
                                'overflowY': 'auto'
                            },
                            style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto',

                            },
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'even'},
                                    'backgroundColor': 'rgb(60,47,47)',
                                },
                                {
                                     'if': {'row_index': 'odd'},
                                     'backgroundColor': 'rgb(50, 50, 50)'
                                },
                                {
                                    'if': {'column_id' : 'Confirmed'},
                                    'color':colors['confirmed_text'],
                                    'fontWeight': 'bold'
                                },
                                {
                                    'if': {'column_id' : 'Deaths'},
                                    'color':colors['deaths_text'],
                                    'fontWeight': 'bold'
                                },
                                {
                                    'if': {'column_id' : 'Recovered'},
                                    'color':colors['recovered_text'],
                                    'fontWeight': 'bold'
                                },
                                ],
                            style_cell_conditional=[
                                {'if': {'column_id': 'State'},
                                 'width': '20%'},
                                {'if': {'column_id': 'Active'},
                                 'width': '20%'},
                                {'if': {'column_id': 'Confirmed'},
                                 'width': '16%'},
                                {'if': {'column_id': 'Deaths'},
                                 'width': '11%'},
                                {'if': {'column_id': 'Recovered'},
                                 'width': '16%'},
                            ],
                
                            data = state_df_latest_stats.to_dict('records'),
                        #filter_action="native",
                            sort_action="native",
                            filter_action='native',
                            editable=True)
                            ]
                        ),


                    
                html.Div(
                    style = { 'width': '96%', 'height': '150%','backgroundColor':colors['background'],
                                'display': 'inline-block',
                                'marginRight': '1.8%', 'verticalAlign': 'top', 'marginTop': '1.3%',  'marginLeft': '1.8%','marginBottom': '1.8%'},
                    children = [
                    html.Div(
                
                        dcc.Graph(id = 'figure_pie', figure = fig_pie)
                      ),
                    ]),
                   
                    html.Div(id='nav-cr-link',children=[                              
                    state_dropdown,
                    html.Div(id='state-total'),# this is is used in app.callback
                    html.Br(),
                    html.Br(),
                    dcc.Graph(id='daily-graphs')
                        ]),
                    ]
                ),
    
    dbc.Container([
    daily_graph_heading2,
        #Table display
        html.Div(
            children=[
                dash_table.DataTable(
                id="district-table",
                columns=[{"name":i, "id": i} for i in state_district_df_disp.columns],
                fixed_rows={'headers': True, 'data': 0},
                
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'lineHeight': '15px'
                },
                style_header={
                    'backgroundColor': 'rgb(30, 30, 30)',
                    'fontWeight': 'bold'
                },
                style_cell={
                                'backgroundColor': 'rgb(100, 100, 100)',
                                'color': '#ffffff',
                                'maxWidth': 0,
                                'fontSize':14,
                                'textAlign': 'center'
                            },
                         
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'even'},
                                    'backgroundColor': 'rgb(60,47,47)',
                                },
                                {
                                     'if': {'row_index': 'odd'},
                                     'backgroundColor': 'rgb(50, 50, 50)'
                                },
                                {
                                    'if': {'column_id' : 'Confirmed'},
                                    'color':colors['confirmed_text'],
                                    'fontWeight': 'bold'
                                },
                                {
                                    'if': {'column_id' : 'Deaths'},
                                    'color':colors['deaths_text'],
                                    'fontWeight': 'bold'
                                },
                                {
                                    'if': {'column_id' : 'Recovered'},
                                    'color':colors['recovered_text'],
                                    'fontWeight': 'bold'
                                },
                                ],
                            style_cell_conditional=[
                                {'if': {'column_id': 'State'},
                                 'width': '20%'},
                                {'if': {'column_id': 'Active'},
                                 'width': '20%'},
                                {'if': {'column_id': 'Confirmed'},
                                 'width': '16%'},
                                {'if': {'column_id': 'Deaths'},
                                 'width': '11%'},
                                {'if': {'column_id': 'Recovered'},
                                 'width': '16%'},
                            ],
                
                # data = district.to_dict('records'),
                #filter_action="native",
                sort_action="native",
                filter_action='native',
                editable=True)
                ]
        ),
    ] ),
     

        
        
      # confiremd and recovered cases
      dbc.Container(children = [
        
         html.Br(),
         dcc.Graph(
             id='cr',
             figure=cr
         ),

        ]
      ),
      
      # conclusion
        html.Br(),
        html.Div( dcc.Markdown('''


            ***Created using*** : Python (Dash, Pandas)

            
            *Source Data* : COVID-19 India Org Data Operations Group,
            Center for Systems Science and Engineering (CSSE) at Johns Hopkins University
            
             *API's used* : 
            * [https://api.covid19india.org]
            * [https://api.rootnet.in]
            * [https://github.com/CSSEGISandData/COVID-19]
           '''
            
           ))

        
        
    
    ]
)

# show total data for each state

@app.callback(
     [Output('state-total', 'children')],
     [Input('select-state', 'value')]
)

def total_of_state(state):
#     country = new_df['Country'].values[0]
    
    # get the state data from state_df
    my_state = state_df_1[state_df_1['State'] == state].loc[:, ['Confirmed', 'Deaths', 'Recovered', 'Active'
    
    ]]
    
    state_total = dbc.Container(id='nav-cr-link',children=
    [   
        html.H4(children='Total case in '+ state + '',style={'textAlign': 'center'}),
        dbc.Row(
            [
                dbc.Col(children = [html.H6('Confirmed',style = {'color': 'black'}), 
                        html.Div(my_state['Confirmed'].sum(), className='text-info', style = {'font-size': '28px', 'font-weight': '700'})],
                        width=3, className='text-center bg-light border-right pt-2', style = {'border-top-left-radius': '6px', 'border-bottom-left-radius': '6px'}),
                
                dbc.Col(children = [html.H6('Recovered', style = {'padding-top': '0px','color': 'black'}),
                        html.Div(my_state['Recovered'].sum(), className='text-success', style = {'font-size': '28px', 'font-weight': '700'})],
                        width=3, className='text-center bg-light border-right pt-2'),
                
                dbc.Col(children = [html.H6('Death', style = {'padding-top': '0px','color': 'black'}), 
                        html.Div(my_state['Deaths'].sum(), className='text-danger', style = {'font-size': '28px', 'font-weight': '700'})],
                        width=3, className='text-center bg-light border-right pt-2'),
                
                dbc.Col(children = [html.H6('Active',style = {'color': 'black'}),
                        html.Div(my_state['Active'].sum(),className='text-warning', style = {'font-size': '28px', 'font-weight': '700'})],
                        width=3, className='text-center bg-light pt-2', style = {'border-top-right-radius': '6px', 'border-bottom-right-radius': '6px'}),
            ]
        , className='mt-1 justify-content-center'),
            
    ]
)
    
    return [state_total]

 #call back function to make change on click

@app.callback(
     Output('daily-graphs', 'figure'),
     [Input('select-state', 'value'),
     Input('select-category','value'),
     Input('select-date', 'value')]
)

def state_wise(state_name, df_type,number):
    # on select of category copy the dataframe to group by country
    if df_type == 'Confirmed cases':
        df_type = df_type_confirmed.copy(deep=True)
        category = 'COVID-19 confirmed cases'
        
    elif df_type == 'Deceased':
        df_type = df_type_Deceased.copy(deep=True)
        
        category = 'COVID-19 Death rate'
        
    else:
        df_type = df_type_Recovered.copy(deep=True)
        
        category = 'COVID-19 recovered cases'
  
   
    # group by state name
    state = df_type.groupby('State')
    """ print(state_name)
    print(category)
    print(number) """
    # select the given country
    state = state.get_group(state_name)
    # print(state)
    
    
    
    state = state.iloc[-number:]
    daily_data = []
    daily_data.append(go.Scatter(
    x=state['Date'], y=state['Value'], name="Covid-19 daily report", line=dict(color='#f36')))
    """ print(daily_data)
    figure = {
         'data': daily_data
        
    } """
    
#    figure=state_daily_graph(state, category)
    return (state_daily_graph(state, category))
    # return (figure)



@app.callback(
     [Output('district-table', 'data')],
     [Input('select-state', 'value')]
)
 
def update_graph(state):
    
    district = state_district_df_disp.groupby('State')
    district_df=district.get_group(state)
    # print(district_df)


    return [
        district_df.to_dict('records')
    ]

  
       


server = app.server



if __name__ == '__main__':
    app.run_server(debug=True)


# In[ ]:




