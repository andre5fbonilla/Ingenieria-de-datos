import pandas as pd
import psycopg2 as psy2
import dash 
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objs as go


dbname = "proyecto"
user = "usuario_posts"
password = "123456"
host = "localhost"

conn = psy2.connect(dbname =dbname, user = user, password = password, host = host)

# Obtener datos de metricas por plataforma de la base de datos
query = """
SELECT 
    p.platform,
    SUM(i.impressions) AS total_impressions,
    SUM(i.reach) AS total_reach,
    SUM(i.likes) AS total_likes,
    SUM(i.num_comments) AS total_comments,
    AVG(i.engagement_rate) AS avg_engagement_rate
FROM 
    posts p
JOIN 
    indicators i ON p.post_ID = i.post_ID
GROUP BY 
    p.platform;
"""
df1 = pd.read_sql(query,conn)


# Obtener datos de participacion por genero y edad
query = """
SELECT 
    a.audience_age,
    a.audience_gender,
    AVG(i.engagement_rate) AS avg_engagement_rate
FROM 
    audience a
JOIN 
    indicators i ON a.post_ID = i.post_ID
GROUP BY 
    a.audience_age, a.audience_gender;
"""
df2 = pd.read_sql(query, conn)

# Obtener datos de participacion por pais
query = """
SELECT 
    a.audience_location AS country,
    AVG(i.engagement_rate) AS avg_engagement_rate
FROM 
    audience a
JOIN 
    indicators i ON a.post_ID = i.post_ID
GROUP BY 
    a.audience_location;
"""
df3 = pd.read_sql(query, conn)

# Obtener datos de participacion del top 10
query ="""
SELECT 
    a.audience_location AS country,
    AVG(i.engagement_rate) AS avg_engagement_rate
FROM 
    audience a
JOIN 
    indicators i ON a.post_ID = i.post_ID
GROUP BY 
    a.audience_location
ORDER BY 
    AVG(i.engagement_rate) DESC
LIMIT 10;
"""
df4 = pd.read_sql(query, conn)


# Obtener datos de participacion por hora de publicacion
query = """
SELECT 
    EXTRACT(hour FROM p.post_timestamp) AS post_hour,
    AVG(i.engagement_rate) AS avg_engagement_rate
FROM 
    posts p
JOIN 
    indicators i ON p.post_ID = i.post_ID
GROUP BY 
    post_hour;
"""
df5 = pd.read_sql(query, conn)

# Obtener datos de participacion por periodo del dia de publicacion
query = """
SELECT 
    p.post_period_time,
    AVG(i.engagement_rate) AS avg_engagement_rate
FROM 
    posts p
JOIN 
    indicators i ON p.post_ID = i.post_ID
GROUP BY 
    p.post_period_time
ORDER BY 
    CASE 
        WHEN p.post_period_time = 'Morning' THEN 1
        WHEN p.post_period_time = 'Afternoon' THEN 2
        ELSE 3
    END;
"""
df6 = pd.read_sql(query, conn)

# Obtener datos de participacion por dia de publicacion
query = """
SELECT 
    TRIM(p.post_day) AS post_day, 
    AVG(i.engagement_rate) AS avg_engagement_rate
FROM 
    posts p
JOIN
    indicators i ON p.post_ID = i.post_id
GROUP BY
    TRIM(p.post_day)
ORDER BY
    CASE 
        WHEN TRIM(p.post_day) = 'Monday' THEN 1
        WHEN TRIM(p.post_day) = 'Tuesday' THEN 2
        WHEN TRIM(p.post_day) = 'Wednesday' THEN 3
        WHEN TRIM(p.post_day) = 'Thursday' THEN 4
        WHEN TRIM(p.post_day) = 'Friday' THEN 5
        WHEN TRIM(p.post_day) = 'Saturday' THEN 6
        WHEN TRIM(p.post_day) = 'Sunday' THEN 7
        ELSE 8 -- en caso de que haya otros valores que no sean días de la semana
    END;
"""
df7 = pd.read_sql(query, conn)

# Obtener datos de indicadores por id de campaña
query = """
SELECT 
    CASE 
        WHEN campaign_ID != 'NULL' THEN 'has_campaign'
        ELSE 'no_campaign'
    END AS campaign_status,
    COUNT(*) AS num_posts,
    AVG(likes) AS avg_likes,
    AVG(num_comments) AS avg_comments,
    AVG(shares) AS avg_shares,
    AVG(impressions) AS avg_impressions,
    AVG(reach) AS avg_reach,
    AVG(engagement_rate) AS avg_engagement_rate
FROM 
    posts p
JOIN 
    indicators i ON p.post_ID = i.post_ID
GROUP BY 
    campaign_status;
"""
df8 = pd.read_sql(query, conn)

# Obtener datos de indicadores id de influencer
query= """SELECT 
    CASE 
        WHEN influencer_ID != 'NULL' THEN 'has_ID'
        ELSE 'no_ID'
    END AS influencer_status,
    COUNT(*) AS num_posts,
    AVG(impressions) AS avg_impressions,
    AVG(reach) AS avg_reach,
    AVG(likes) AS avg_likes,
    AVG(num_comments) AS avg_comments,
    AVG(shares) AS avg_shares,
    AVG(engagement_rate) AS avg_engagement_rate
FROM 
    posts p
JOIN 
    indicators i ON p.post_ID = i.post_ID
GROUP BY 
    influencer_status;
"""
df9 = pd.read_sql(query, conn)

# Obtener datos de indicadores por tipo de publicacion
query ="""
SELECT 
    p.post_type,
    COUNT(*) AS num_posts,
    SUM(impressions) AS total_impressions,
    SUM(reach) AS total_reach,
    SUM(likes) AS total_likes,
    SUM(num_comments) AS total_comments,
    SUM(shares) AS total_shares,
    AVG(engagement_rate) AS avg_engagement_rate
FROM 
    posts p
JOIN 
    indicators i ON p.post_ID = i.post_ID
GROUP BY 
    post_type
"""
df10 = pd.read_sql(query, conn)

# Obtener datos de indicadores por sentimiento de la publicacion
query ="""
SELECT 
    p.sentiment,
    COUNT(*) AS num_posts,
    AVG(impressions) AS total_impressions,
    AVG(reach) AS total_reach,
    AVG(likes) AS total_likes,
    AVG(num_comments) AS total_comments,
    AVG(shares) AS total_shares,
    AVG(engagement_rate) AS avg_engagement_rate
FROM 
    posts p
JOIN 
    indicators i ON p.post_ID = i.post_ID
GROUP BY 
    sentiment
"""
df11 = pd.read_sql(query, conn)

# Cerrar la conexión
conn.close()

# Crear la aplicación Dash
app = dash.Dash(__name__)


# Crear diagrama de barras de metricas por plataforma
fig1 = px.bar(df1, x='platform', y=['total_impressions', 'total_reach', 'total_likes', 'total_comments'], 
             title='Cantidad de Likes, Comentarios, Impresiones y Alcance por Plataforma', 
             labels={'value': 'Cantidad', 'variable': 'Métrica'},
             barmode='group'
             )

# Crear el gráfico de pie de participacion promedio por plataforma
fig2 = px.pie(df1, names='platform', values='avg_engagement_rate', title='Tasa de Participación Promedio por Plataforma')

# Crear el gráfico de barras apiladas para edad y género del público objetivo y su tasa de participación promedio
fig3 = px.bar(df2, x='audience_age', y='avg_engagement_rate', color='audience_gender', 
                title='Tasa de Participación Promedio por Edad y Género del Público Objetivo', 
                labels={'audience_age': 'Edad', 'avg_engagement_rate': 'Tasa de Participación Promedio', 'audience_gender': 'Género'}, 
                barmode='stack'
                )

# Crear el mapa de calor para el engagement rate promedio por país
fig4 = px.choropleth(df3, locations='country', locationmode='country names', color='avg_engagement_rate', 
                        title='Tasa de Participación Promedio por País', 
                        labels={'country': 'País', 'avg_engagement_rate': 'Tasa de Participación Promedio'},
                        color_continuous_scale=px.colors.sequential.Plasma
                        )

# Crear diagrama de barras del top 10 de paises
fig5 = px.bar(df4, x='avg_engagement_rate', y='country', 
             title='Top 10 Paises por Promedio de Tasa de Participación', 
             labels={'value': 'Cantidad', 'variable': 'Tasa de Participación'}
             )


# Crear el gráfico de líneas para la relación entre la hora de publicación y la tasa de participación
fig6 = px.line(df5, x='post_hour', y='avg_engagement_rate', 
                title='Tasa de Participación Promedio por Hora de Publicación', 
                labels={'post_hour': 'Hora de Publicación', 'avg_engagement_rate': 'Tasa de Participación Promedio'}
                )

# Crear el gráfico de líneas para la relación entre el periodo de tiempo del post y la tasa de participación
fig7 = px.line(df6, x='post_period_time', y='avg_engagement_rate', 
                title='Tasa de Participación Promedio por Periodo de Tiempo del Post', 
                labels={'post_period_time': 'Periodo de Tiempo', 'avg_engagement_rate': 'Tasa de Participación Promedio'}
                )

# Crear el gráfico de líneas para la relación entre el dia del post y la tasa de participación
fig8 = px.line(df7, x='post_day', y='avg_engagement_rate',
               title='Tasa de Participación Promedio por Día de Publicación',
               labels={'post_day':'Día de Publicación', 'avg_engagement_rate':'Tasa de Participación Promedio'}
               )

# Crear el diagrama de barras de cantidad de posts con y sin campaña
fig9 = px.bar(df8, x='num_posts', y='campaign_status',
              title='Cantidad de posts con y sin campaña publicitaria',
              labels={'value':'Cantidad','variable':'Estado'}
            )

# Crear el diagrama de barras de metricas de post con campaña de publicidad y sin
fig10 = px.bar(df8, x='campaign_status', y=['avg_impressions','avg_reach','avg_likes', 'avg_comments', 'avg_shares','avg_engagement_rate'], 
             title='Promedio de Indicadores de Posts con y sin Campaña de Publicidad', 
             labels={'value': 'Cantidad', 'variable': 'Métrica'},
             barmode='group'
             )

# Crear el diagrama de barras de cantidad de posts con y sin influencer
fig11 = px.bar(df9, x='num_posts', y='influencer_status',
              title='Cantidad de posts con y sin Influencer asociado',
              labels={'value':'Cantidad','variable':'Estado'}
            )

# Crear el diagrama de barras de metricas de post con influencer y sin
fig12 = px.bar(df9, x='influencer_status', y=['avg_impressions','avg_reach','avg_likes', 'avg_comments', 'avg_shares','avg_engagement_rate'], 
             title='Promedio de Indicadores de Posts con y sin Influencer asociado', 
             labels={'value': 'Cantidad', 'variable': 'Métrica'},
             barmode='group'
             )

# Crear el gráfico de pie de participacion promedio por plataforma
fig13 = px.pie(df10, names='post_type', values='num_posts', title='Cantidad de Publicaciones de cada Tipo')

# Crear el diagrama de barras de metricas por tipo de post
fig14 = px.bar(df10, x='post_type', y=['total_impressions','total_reach','total_likes', 'total_comments', 'total_shares','avg_engagement_rate'], 
             title='Indicadores por Tipo de Publicación', 
             labels={'value': 'Cantidad', 'variable': 'Tipo de Publicación'},
             barmode='group'
             )

# Crear el diagrama de pie de cantidad por sentimento
fig15 = px.pie(df11, names='sentiment', values='num_posts', title='Cantidad de Publicaciones por Sentimiento')

# Crear el diagrama de barras de indicadores por sentimento
fig16 = px.bar(df11, x='sentiment', y=['total_impressions','total_reach','total_likes', 'total_comments', 'total_shares','avg_engagement_rate'], 
             title='Indicadores por Sentimiento de Publicación', 
             labels={'value': 'Cantidad', 'variable': 'Tipo de Publicación'},
             barmode='group'
             )

# Definir el layout de la aplicación Dash
app.layout = html.Div(children=[
    html.H1(children='Análisis de Redes Sociales'),

    html.Div(children=[
        html.H2(children='Indicadores por Plataforma'),
        dcc.Graph(
            id='bar-graph-indicators',
            figure=fig1
        ),
        dcc.Graph(
            id='pie-graph-egagement-platform',
            figure=fig2
        )
    ]),

    html.Div(children=[
        html.H2(children='Tasa de Participación Promedio por Edad y Género del Público Objetivo'),
        dcc.Graph(
            id='scatter-graph-engagement-public',
            figure=fig3
        )
    ]),

    html.Div(children=[
        html.H2(children='Tasa de participacion Promedio por País'),
        dcc.Graph(
            id='heatmap-graph-engagement-nation',
            figure=fig4
        ),
        dcc.Graph(
            id='bar-graph-top-10',
            figure=fig5
        )
        ]),

    html.Div(children=[
        html.H2(children='Tasa de Participación Promedio por hora y fecha de Publicación'),
        dcc.Graph(
            id='line-graph-post-time',
            figure=fig6
        ),
        dcc.Graph(
            id='line-graph-post-period-time',
            figure=fig7
        ),
        dcc.Graph(
            id='line-graph-post-day',
            figure=fig8
        )
    ]),

    html.Div(children=[
        html.H2(children='Publicaciones Relacionados con Campaña Publicitaria'),
        dcc.Graph(
            id='bar-graph-cant-campaign',
            figure=fig9
        ),
        dcc.Graph(
            id='bar-graph-campaign',
            figure=fig10
        )
        ]),

    html.Div(children=[
        html.H2(children='Publicaciones Relacionadas con Influencers'),
        dcc.Graph(
            id='bar-graph-cant-influencers',
            figure=fig11
        ),
        dcc.Graph(
            id='bar-graph-influencers',
            figure=fig12
        )
        ]),
        html.Div(children=[
        html.H2(children='Indicadores por Tipo de Publicación'),
        dcc.Graph(
            id='pie-graph-cant',
            figure=fig13
        ),
        dcc.Graph(
            id='bar-graph-type',
            figure=fig14
        )
    ]),
    html.Div(children=[
        html.H2(children='Publicaciones por Sentimiento Expresado'),
        dcc.Graph(
            id='pie-graph-cant-sentiment',
            figure=fig15
        ),
        dcc.Graph(
            id='bar-graph-sentiment',
            figure=fig16
        )
        ]),

])


# Ejecutar la aplicación

if __name__ == '__main__' :
    app.run_server(port=8085)