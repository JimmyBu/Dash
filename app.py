import dash
from dash import dcc
from dash import html
from dash import dash_table
import pandas as pd
import mysql.connector
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import json
from appConst import appConst as AppConst


# MySQL connection
def create_conn():
    conn = mysql.connector.connect(
        host=AppConst.DBConst.db_connect_host,
        user=AppConst.DBConst.db_connect_user_name,
        port=AppConst.DBConst.db_connect_port,
        password=AppConst.DBConst.db_connect_password,
        database=AppConst.DBConst.db_connect_db_name
    )
    return conn


# Fetch data from a table
def fetch_table_data(table_name, query=None):
    conn = create_conn()
    if query is None:
        query = f'SELECT * FROM {table_name}'
    df = pd.read_sql(query, conn)
    conn.close()
    return df


# Example: Generate charts for the 'Champion' and 'Item' tables
champion_df = fetch_table_data('Champion')
item_df = fetch_table_data('Item')

champion_query = f"""
SELECT
    Champion.championID as ID,
    Champion.name as Name,
    Champion.title as Alias,
    Champion.blurb as Description,
    Champion.partype as Story,
    Champion.difficulty as Difficulty,
    Champion.tag as Role,
    CI.baseAttack,
    CI.baseDefense,
    CI.baseMagic,
    CI.hp,
    CI.hpPerLevel,
    CI.mp,
    CI.mpPerLevel,
    CI.moveSpeed,
    CI.armor,
    CI.armorPerLevel,
    CI.spellBlock,
    CI.spellBlockPerLevel,
    CI.attackRange,
    CI.hpRegen,
    CI.hpRegenPerLevel,
    CI.mpRegen as mpRegeneration,
    CI.mpRegenPerLevel as mpRegernerationPerLevel,
    CI.attackDamage,
    CI.attackDamagerPerLevel,
    CI.attackSpeedPerLevel,
    CI.attackSpeed
FROM 
  Champion 
JOIN ChampionInfo CI on Champion.championID = CI.championID;
"""
ChampionInfo = fetch_table_data('Champion', query=champion_query)


def fetch_user_history_data(lol_id):
    conn = create_conn()
    user_history_query = f"""
    SELECT
      TPI.gameID,
      CASE
        WHEN Team.win = true THEN 'win'
        WHEN Team.win = false THEN 'lose'
      END as Outcome,
      CASE
        WHEN TPI.teamID = 100 THEN 'Blue'
        WHEN TPI.teamID = 200 THEN 'Red'
      END as Team,
      TPI.participantID as PlayerNumber,
      Champion.name as ChampionName,
      TP.lane as lane,
      TP.role,
      Item0.name as FirstItemName,
      Item1.name as SecondItemName,
      Item2.name as ThirdItemName,
      Item3.name as FourthItemName,
      Item4.name as FifthItemName,
      Item5.name as SixthItemName
    FROM
      PlayerInfo
    JOIN
      TeamParticipantInfo TPI ON PlayerInfo.summonerID = TPI.summonerID
    JOIN
      Team ON Team.gameID = TPI.gameID AND Team.teamID = TPI.teamID
    JOIN
      TeamParticipants TP ON TPI.gameID = TP.gameID AND TP.summonerID = TPI.summonerID
    JOIN
      Champion ON TP.championID = Champion.championID
    JOIN
      Item as Item0 ON TPI.item0 = Item0.itemID
    JOIN
      Item as Item1 ON TPI.item1 = Item1.itemID
    JOIN
      Item as Item2 ON TPI.item2 = Item2.itemID
    JOIN
      Item as Item3 ON TPI.item3 = Item3.itemID
    JOIN
      Item as Item4 ON TPI.item4 = Item4.itemID
    JOIN
      Item as Item5 ON TPI.item5 = Item5.itemID
    WHERE PlayerInfo.lolID = {lol_id};
    """
    user_history_df = fetch_table_data('PlayerInfoMatchHistory', query=user_history_query)
    conn.close()
    return user_history_df


def fetch_UserInfo(lol_id):
    conn = create_conn()
    UserInfoQuery = f"SELECT summonerName FROM PlayerInfo WHERE lolID = {lol_id};"
    userInfo_df = fetch_table_data('PlayerInfo', query=UserInfoQuery)
    conn.close()
    return userInfo_df


def fetch_KDA(lol_id):
    conn = create_conn()
    KDA_query = f"""
    SELECT
        SUM(TPI.kills) AS kills,
        SUM(TPI.deaths) AS deaths,
        SUM(TPI.assists) AS assists,
        SUM(TPI.doubleKills) AS doubleKills,
        SUM(TPI.tripleKills) AS tripleKills,
        SUM(TPI.quadraKills) AS quadraKills,
        SUM(TPI.pentaKills) AS pentaKills
    FROM TeamParticipantInfo TPI
    JOIN PlayerInfo ON PlayerInfo.summonerID = TPI.summonerID
    JOIN TeamParticipants TP ON TPI.gameID = TP.gameID AND TP.summonerID = TPI.summonerID
    JOIN Champion ON TP.championID = Champion.championID
    WHERE lolID = {lol_id};
    """
    KDA_df = fetch_table_data('PlayerInfo', query=KDA_query)
    conn.close()
    return KDA_df


def fetch_Usage(lol_id):
    conn = create_conn()
    Usage_query = f"""
    SELECT
      Champion.name as ChampionName,
      count(Champion.name) as ChampionUsage
    FROM
      PlayerInfo
    JOIN
      TeamParticipantInfo TPI ON PlayerInfo.summonerID = TPI.summonerID
    JOIN
      Team ON Team.gameID = TPI.gameID AND Team.teamID = TPI.teamID
    JOIN
      TeamParticipants TP ON TPI.gameID = TP.gameID AND TP.summonerID = TPI.summonerID
    JOIN
      Champion ON TP.championID = Champion.championID
    JOIN
      Item as Item0 ON TPI.item0 = Item0.itemID
    JOIN
      Item as Item1 ON TPI.item1 = Item1.itemID
    JOIN
      Item as Item2 ON TPI.item2 = Item2.itemID
    JOIN
      Item as Item3 ON TPI.item3 = Item3.itemID
    JOIN
      Item as Item4 ON TPI.item4 = Item4.itemID
    JOIN
      Item as Item5 ON TPI.item5 = Item5.itemID
    WHERE PlayerInfo.lolID = {lol_id}
    GROUP BY Champion.name;
    """
    Usage_df = fetch_table_data('PlayerInfo', query=Usage_query)
    conn.close()
    return Usage_df


def fetch_match_data(lol_id, game_id):
    conn = create_conn()
    match_query = f"""
    SELECT
      TPI.gameID,
      CASE
        WHEN Team.win = true THEN 'win'
        WHEN Team.win = false THEN 'lose'
      END as Outcome,
      CASE
        WHEN TPI.teamID = 100 THEN 'Blue'
        WHEN TPI.teamID = 200 THEN 'Red'
      END as Team,
      TPI.participantID as PlayerNumber,
      Champion.name as ChampionName,
      TP.lane as lane,
      TP.role,
      Item0.name as FirstItemName,
      Item1.name as SecondItemName,
      Item2.name as ThirdItemName,
      Item3.name as FourthItemName,
      Item4.name as FifthItemName,
      Item5.name as SixthItemName
    FROM
      PlayerInfo
    JOIN
      TeamParticipantInfo TPI ON PlayerInfo.summonerID = TPI.summonerID
    JOIN
      Team ON Team.gameID = TPI.gameID AND Team.teamID = TPI.teamID
    JOIN
      TeamParticipants TP ON TPI.gameID = TP.gameID AND TP.summonerID = TPI.summonerID
    JOIN
      Champion ON TP.championID = Champion.championID
    JOIN
      Item as Item0 ON TPI.item0 = Item0.itemID
    JOIN
      Item as Item1 ON TPI.item1 = Item1.itemID
    JOIN
      Item as Item2 ON TPI.item2 = Item2.itemID
    JOIN
      Item as Item3 ON TPI.item3 = Item3.itemID
    JOIN
      Item as Item4 ON TPI.item4 = Item4.itemID
    JOIN
      Item as Item5 ON TPI.item5 = Item5.itemID
    WHERE PlayerInfo.lolID = {lol_id} and TPI.gameID = {game_id};
    """
    match_df = fetch_table_data('MatchHistory', query=match_query)
    conn.close()
    return match_df


# Generate the user history layout
def generate_user_history_layout(lol_id):
    user_history_df = fetch_user_history_data(lol_id)
    UserInfo = fetch_UserInfo(lol_id)
    Usage = fetch_Usage(lol_id)
    KDA = fetch_KDA(lol_id)
    user_history_table = dash_table.DataTable(
        id='user-history-table',
        columns=[{"name": i, "id": i} for i in user_history_df.columns],
        data=json.loads(user_history_df.to_json(orient='records')),
        style_cell={'textAlign': 'left'},
        style_header={'fontWeight': 'bold'},
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}
        ]
    )
    user_name = UserInfo['summonerName'].iloc[0]
    num_rows = len(user_history_df)
    Kills = int(KDA['kills'].iloc[0])
    Deaths = int(KDA['deaths'].iloc[0])
    Assists = int(KDA['assists'].iloc[0])
    doubleKills = int(KDA['doubleKills'].iloc[0])
    tripleKills = int(KDA['tripleKills'].iloc[0])
    quadraKills = int(KDA['quadraKills'].iloc[0])
    pentaKills = int(KDA['pentaKills'].iloc[0])
    win_rate = f"{user_history_df[user_history_df['Outcome'] == 'win'].shape[0] / num_rows:.1%}"
    top = user_history_df[user_history_df['lane'] == 'TOP'].shape[0]
    mid = user_history_df[user_history_df['lane'] == 'MIDDLE'].shape[0]
    bottom = user_history_df[user_history_df['lane'] == 'BOTTOM'].shape[0]
    jungle = user_history_df[user_history_df['lane'] == 'JUNGLE'].shape[0]
    support = user_history_df[user_history_df['lane'] == 'NONE'].shape[0]
    DUO = user_history_df[user_history_df['role'] == 'DUO'].shape[0]
    SOLO = user_history_df[user_history_df['role'] == 'SOLO'].shape[0]
    DUO_CARRY = user_history_df[user_history_df['role'] == 'DUO_CARRY'].shape[0]
    DUO_SUPPORT = user_history_df[user_history_df['role'] == 'DUO_SUPPORT'].shape[0]
    JUNGLE = user_history_df[user_history_df['role'] == 'NONE'].shape[0]
    sorted_df = Usage.sort_values('ChampionUsage', ascending=False)
    top_6_df = sorted_df.head(6)

    # Define the data for the pie chart
    pie_data_champion = [
        go.Pie(
            labels=top_6_df['ChampionName'],
            values=top_6_df['ChampionUsage'],
            hole=0.4,
            hoverinfo='label+percent',
            textinfo='label+value',
            marker=dict(colors=['#FFC0CB', '#FF69B4', '#FF1493', '#C71585', '#9400D3', '#4B0082'])

        )
    ]

    pie_data_lane = [
        go.Pie(
            labels=['Top', 'Mid', 'Bottom', 'Jungle', 'None (support)'],
            values=[top, mid, bottom, jungle, support],
            hole=0.4,
            hoverinfo='label+percent',
            textinfo='label+value',
            marker=dict(colors=['#FFC0CB', '#FF69B4', '#FF1493', '#C71585', '#4B0082'])
        )
    ]

    return html.Div([
        html.H1(f"User Info of: {user_name}"),
        html.H4(f"Your League of Legend ID: {lol_id}"),
        html.H4(f"Number of Games Played: {num_rows}"),
        html.H4(f"Total Kills: {Kills}"),
        html.H4(f"Total Deaths: {Deaths}"),
        html.H4(f"Total Assists: {Assists}"),
        html.H4(f"Total Double Kills: {doubleKills}"),
        html.H4(f"Total Triple Kills: {tripleKills}"),
        html.H4(f"Total Quadra Kills: {quadraKills}"),
        html.H4(f"Total Penta Kills: {pentaKills}"),
        html.H4(f"Win Rate: {win_rate}"),
        html.H4(f"Role Distribution : DUO: {DUO}, SOLO: {SOLO}, DUO_CARRY: {DUO_CARRY}, DUO_SUPPORT: {DUO_SUPPORT}, "
                f"JUNGLE: {JUNGLE}"),
        html.H6(f"The Champion pie chart only contains the top 6 usage champions", style={'text-align': 'center'}),
        dcc.Graph(id='pie-chart', figure={'data': pie_data_champion}),
        dcc.Graph(id='pie-chart', figure={'data': pie_data_lane}),
        user_history_table,
        dcc.Input(id='game-id-input', type='number', placeholder='Enter Game ID'),
        html.Button('Go', id='game-go-button'),
        html.Br(),
        dcc.Link("Back to enter League of Legend ID", href="/user"),
    ])


def game_layout(lol_id, game_id):
    match = fetch_match_data(lol_id, game_id)
    match_table = dash_table.DataTable(
        id='user-history-table',
        columns=[{"name": i, "id": i} for i in match.columns],
        data=json.loads(match.to_json(orient='records')),
        style_cell={'textAlign': 'left'},
        style_header={'fontWeight': 'bold'},
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}
        ]
    )
    return html.Div([
        match_table,
        dcc.Link("Back to User", href=f"/user/{lol_id}"),
    ])


champion_info_table = dash_table.DataTable(
    id='champion-info-table',
    columns=[{"name": i, "id": i} for i in ChampionInfo.columns],
    data=json.loads(ChampionInfo.to_json(orient='records')),
    style_cell={'textAlign': 'left'},
    style_header={'fontWeight': 'bold'},
)

item_info_table = dash_table.DataTable(
    id='item-info-table',
    columns=[{"name": i, "id": i} for i in item_df.columns],
    data=json.loads(item_df.to_json(orient='records')),
    style_cell={'textAlign': 'left'},
    style_header={'fontWeight': 'bold'},
)

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Create the home layout
home_layout = html.Div([
    html.H1("League of Legend"),
    html.Div(dcc.Link("Champion Info", href="/champion")),
    html.Div(dcc.Link("Item Info", href="/item")),
    html.Div(dcc.Link("Match Data Initial View", href="/user")),
])

champion_layout = html.Div([
    html.H1("Champion Info"),
    dcc.Link("HOME", href="/"),
    champion_info_table,
])

item_layout = html.Div([
    html.H1("Item Info"),
    dcc.Link("HOME", href="/"),
    item_info_table,
])

user_layout = html.Div([
    html.H1("Provide your League of Legend ID"),
    dcc.Link("HOME", href="/"),
    html.Br(),
    dcc.Input(id='lol-id-input', type='number', placeholder='Enter LOL ID'),
    html.Button('Go', id='go-button'),
])

# App layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    html.Div([
        dcc.Input(id='lol-id-input', type='number', placeholder='Enter LOL ID', style={"display": "none"}),
        html.Button('Go', id='go-button', style={"display": "none"})
    ]),
    html.Div([
        dcc.Input(id='game-id-input', type='number', placeholder='Enter Game ID', style={"display": "none"}),
        html.Button('Go', id='game-go-button', style={"display": "none"})
    ]),
])


# Callback to update the layout based on the URL
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/champion':
        return champion_layout
    elif pathname == '/item':
        return item_layout
    elif pathname == '/user':
        return user_layout
    elif pathname.startswith('/user/'):
        lol_id = pathname.split('/')[-1]
        return generate_user_history_layout(lol_id)
    if pathname.startswith(f'/match'):
        lol_id, game_id = pathname.split('/')[-2:]
        return game_layout(lol_id, game_id)
    else:
        return home_layout


@app.callback(
    [Output('url', 'pathname'), Output('lol-id-input', 'value')],
    [Input('go-button', 'n_clicks'), Input('game-go-button', 'n_clicks'), Input('url', 'pathname')],
    [State('lol-id-input', 'value'), State('game-id-input', 'value'), State('url', 'pathname')],
    prevent_initial_call=True
)
def go_to_Summoner_Info(n_clicks, game_n_clicks, pathname, lol_id, game_id, current_pathname):
    if pathname != current_pathname:
        current_pathname = pathname
    ctx = dash.callback_context
    if ctx.triggered[0]['prop_id'] == 'go-button.n_clicks':
        return f"/user/{lol_id}", lol_id
    if ctx.triggered[0]['prop_id'] == 'game-go-button.n_clicks':
        if game_id is not None and game_id != '':
            lol_id = current_pathname.split('/')[-1]
            return f"/match/{lol_id}/{game_id}", lol_id
    return dash.no_update, lol_id


@app.callback(Output('input-container', 'children'),
              Input('url', 'pathname'),
              State('lol-id-input', 'value'))
def update_input_container(pathname, lol_id):
    if pathname == '/match':
        return [dcc.Input(id='lol-id-input', type='number', placeholder='Enter LOL ID'),
                html.Button('Go', id='go-button')]
    elif pathname == f"/user/{lol_id}":
        return [dcc.Input(id='game-id-input', type='number', placeholder='Enter Game ID'),
                html.Button('Go', id='game-go-button')]
    return []


if __name__ == '__main__':
    app.run_server(debug=True)
