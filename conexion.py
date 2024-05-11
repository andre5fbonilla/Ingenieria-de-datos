import pandas as pd
import psycopg2 as psy2
import dash 
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash import dash_table

dbname = "proyecto"
user = "usuario_posts"
password = "123456"
host = "localhost"

conn = psy2.connect(dbname =dbname, user = user, password = password, host = host)

sql_query = "Select * from posts LIMIT 10;"

df =pd.read_sql(sql_query, conn)

conn.close()

app =dash.Dash()
app.layout = html.Div(children=[
    html.H1(children='Prueba de conexión', style={'fontSize': 36,'textAlign': 'center'}),
    html.H2(children='Primeras 10 filas de la tabla "posts"',style={'textAlign': 'center'}),
    dash_table.DataTable(
        id='tabla-datos',
        columns = [{'name': col, 'id': col} for col in df.columns],
        data = df.to_dict('records'),
        style_header = {'backgroundColor': '#4f81bd','fontWeight': 'bold','fontSize': 15,'textAlign': 'center'},
        style_cell = {'textAlign': 'left'},
        style_cell_conditional = [{
            'if': {'row_index': 'odd'},  
            'backgroundColor': '#dde5ef','fontWeight': 'bold'}, 
            {
            'if': {'row_index': 'even'},  
            'backgroundColor': 'white','fontWeight': 'bold'}
            ]
        
    )
])


conn.close()

if __name__ == '__main__' :
    app.run_server(port=8085)