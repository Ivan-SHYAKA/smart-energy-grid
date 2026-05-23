import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import time
from sqlalchemy import create_engine, text

DB_URL = "postgresql://postgres:Forev%4012345@localhost:5432/energy_db"

def get_engine():
    return create_engine(DB_URL)

app = dash.Dash(__name__)

app.layout = html.Div(style={'fontFamily': 'sans-serif', 'padding': '20px'}, children=[
    html.H1("Smart Energy Grid Dashboard", style={'textAlign': 'center'}),

    html.H2("Real-time readings — last hour"),
    dcc.Graph(id='realtime'),

    html.H2("Daily pattern — today vs yesterday"),
    dcc.Graph(id='daily'),

    html.H2("Weekly energy trend"),
    dcc.Graph(id='weekly'),

    html.H2("Monthly usage by region"),
    dcc.Graph(id='regional'),

    html.H2("Performance metrics"),
    html.Div(id='perf'),

    dcc.Interval(id='tick', interval=30_000, n_intervals=0),
])

@app.callback(Output('realtime','figure'), Input('tick','n_intervals'))
def update_realtime(_):
    engine = get_engine()
    df = pd.read_sql("""
        SELECT time_bucket('5 minutes', timestamp) AS bucket,
               AVG(power) as avg_power
        FROM energy_readings
        WHERE timestamp >= NOW() - INTERVAL '1 hour'
        GROUP BY bucket ORDER BY bucket
    """, engine)
    engine.dispose()
    return px.line(df, x='bucket', y='avg_power',
                   title='Average grid power — last 60 minutes',
                   labels={'bucket': 'Time', 'avg_power': 'Avg Power (W)'})

@app.callback(Output('daily','figure'), Input('tick','n_intervals'))
def update_daily(_):
    engine = get_engine()
    df = pd.read_sql("""
        SELECT time_bucket('1 hour', timestamp) AS hour,
               AVG(power) as avg_power,
               DATE_TRUNC('day', timestamp)::date::text as day
        FROM energy_readings
        WHERE timestamp >= NOW() - INTERVAL '2 days'
        GROUP BY hour, day ORDER BY hour
    """, engine)
    engine.dispose()
    return px.line(df, x='hour', y='avg_power', color='day',
                   title='Hourly pattern — today vs yesterday')

@app.callback(Output('weekly','figure'), Input('tick','n_intervals'))
def update_weekly(_):
    engine = get_engine()
    df = pd.read_sql("""
        SELECT bucket,
               SUM(total_energy) as total_kwh
        FROM energy_readings_daily
        WHERE bucket >= NOW() - INTERVAL '7 days'
        GROUP BY bucket ORDER BY bucket
    """, engine)
    engine.dispose()
    df['day'] = df['bucket'].dt.strftime('%Y-%m-%d')
    return px.bar(df, x='day', y='total_kwh',
                  title='Daily energy (kWh) — last 7 days')

@app.callback(Output('regional','figure'), Input('tick','n_intervals'))
def update_regional(_):
    engine = get_engine()
    df = pd.read_sql("""
        SELECT LEFT(meter_id::text, 1) AS region,
               SUM(total_energy) as total_kwh
        FROM energy_readings_daily
        WHERE bucket >= NOW() - INTERVAL '30 days'
        GROUP BY region ORDER BY region
    """, engine)
    engine.dispose()
    return px.bar(df, x='region', y='total_kwh',
                  title='Monthly energy by region (first digit of meter ID)',
                  labels={'region': 'Region', 'total_kwh': 'Total Energy (kWh)'})

@app.callback(Output('perf','children'), Input('tick','n_intervals'))
def update_perf(_):
    engine = get_engine()

    t0 = time.time()
    with engine.connect() as conn:
        conn.execute(text("""
            SELECT AVG(power) FROM energy_readings
            WHERE timestamp >= NOW() - INTERVAL '1 day'
        """)).fetchall()
    raw_ms = (time.time() - t0) * 1000

    t0 = time.time()
    with engine.connect() as conn:
        conn.execute(text("""
            SELECT AVG(avg_power) FROM energy_readings_hourly
            WHERE bucket >= NOW() - INTERVAL '1 day'
        """)).fetchall()
    agg_ms = (time.time() - t0) * 1000

    engine.dispose()
    speedup = raw_ms / agg_ms if agg_ms > 0 else 0

    return html.Div([
        html.H3("Query performance comparison"),
        html.P(f"Raw query (1 day scan): {raw_ms:.0f} ms"),
        html.P(f"Continuous aggregate query: {agg_ms:.0f} ms"),
        html.P(f"Speedup: {speedup:.1f}x faster"),
        html.H3("Storage efficiency (after compression)"),
        html.P("energy_readings (1d chunks): 780 MB → 397 MB (1.96x ratio)"),
        html.P("energy_readings_3h: 791 MB → 412 MB (1.92x ratio)"),
        html.P("energy_readings_week: 710 MB → 360 MB (1.97x ratio)"),
    ])

if __name__ == '__main__':
    app.run(debug=True, port=8050)