import pandas as pd
import json, math
import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_table
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.UNITED])


# --------------------
# Import data
tsne = pd.read_csv('data/tsne_data.csv', sep='\t')

# --------------------
# Plotly graph
tsne_fig = px.scatter(

    tsne,
    x='x', y='y',
    color='genre',
    hover_name='title',
    height=600,
    width=800,
    hover_data={
        'x':False,
        'y':False,
        'author':True,
        'date':True
    }
)

# --------------------
# Various metadata

# Books by author
metadata = pd.read_csv('data/metadata.tsv', sep='\t', index_col=0)
metadata['label'] = metadata.title + ' - ' + metadata.author
# clean up the genre column a bit for viewing
metadata['genre'] = metadata.genre.str.replace('|', ', ').str.lower().fillna('(none)')

def getAuthorTable(author='Chandler, Raymond'):

    return metadata[metadata.author == author][['title', 'date', 'genre']]


# Confidence scores by title
columns = ['adventure', 'detective and mystery', 'domestic', 'fantasy', 'historical', 
          'horror', 'political', 'religious', 'romance', 'science fiction', 'war stories', 'westerns']
scores_df = pd.read_csv('data/scores.tsv', sep='\t', index_col=0)
scores_df.columns = columns

# This is statistically dubious, but we render confidence as 0-1 for readability
def probaConvert(x):
    return 1 / (1 + math.exp(-x))

scores_df = scores_df.applymap(probaConvert)

# --------------------
# confidence chart

def generateConfidenceFig(book_id=10889):

    confidence_fig = go.Figure(
                        go.Bar(
                            x=scores_df.loc[book_id].sort_values(),
                            y=[scores_df.columns[i] for i in scores_df.loc[book_id].argsort()],
                            orientation='h'
                            ),
                    )
    confidence_fig.add_shape(type='line', layer='below',
                    x0=.5, y0=-1, x1=.5, y1=12,
                    line=dict(
                        color='RoyalBlue',
                        width=3,
                        dash='dot',
                    )
                )
    confidence_fig.update_layout(
        margin=dict(t=20, b=20),
        autosize=False
    )
    return confidence_fig
confidence_fig = generateConfidenceFig(10889)

# --------------------
# Table of feature coefficients
with open('data/top_100_words.json', 'r') as file:
    topwords = json.load(file)

def generateWordsTable(genre='detective and mystery', max_rows=15):

    df1 = pd.DataFrame(topwords[genre][0], columns=['word (+)', 'coefficient (+)'])
    df2 = pd.DataFrame(topwords[genre][1], columns=['word (-)', 'coefficient (-)'])
    df = pd.concat([df1, df2], axis=1)
    df['coefficient (+)'] = df['coefficient (+)'].round(3)
    df['coefficient (-)'] = df['coefficient (-)'].round(3)
    df = df[:max_rows]

    return df

# default dataframe
words_df = generateWordsTable()  

# ---------------------
# Bootstrap Cards

title_card = dbc.Card(

    dbc.CardBody([
        html.H1(
            "9,089 American Novels, 1880-2000",
        ),
    
        html.H6(
            "Automatic Genre Classification for the US Novel Corpus",
            className='card-subtitle',
            style={
                'justify':'center'
            }
        ),

    ]),

)

projection_card = dbc.Card(

    dbc.CardBody([
        dcc.Graph(
            id='tsne_projection', 
            figure=tsne_fig),
    ]),
    color='dark'
)

author_card = dbc.Card(
                
    dbc.CardBody([
        html.H5('Search by Author', className='card-title'),
        dcc.Dropdown(
            id='author-select',
            options=[{'label': author, 'value': author} for author in metadata.author.unique()],
            value='Chandler, Raymond',
            style={
                'margin-top':10,
                'margin-bottom': 20
            }
        ),
        dash_table.DataTable(
            id='authors-table',
            columns=[{"name": i, "id": i} for i in ['title', 'date', 'genre']],
            data=getAuthorTable('Chandler, Raymond').to_dict('records'),
            style_cell={'padding' : '8px'}
        )
    ]),
)

confidence_card = dbc.Card(
                
    dbc.CardBody([
        html.H5('Genre Probabilities', className='card-title'),
        dcc.Dropdown(
            id='title-select',
            options=[{'label': metadata.loc[i].label, 'value': i} for i in scores_df.index],
            value=10889,
            style={
                'margin-top': 20,
            }
        ),
        dcc.Graph(
            id='confidence-fig',
            figure=confidence_fig,
            config={
                'displayModeBar': False
            }
        )
       
    ]),
)

words_card = dbc.Card(

    dbc.CardBody([
        html.H5('Top Words For Each Genre', className='card-title'),
        dcc.Dropdown(
            id='genre-select',
            options=[{'label': genre, 'value': genre} for genre in topwords],
            value='detective and mystery',
            style={
                'margin-bottom':10
            }
        ),
        dash_table.DataTable(
            id='words-table',
            columns=[{"name": i, "id": i} for i in words_df.columns],
            data=words_df.to_dict('records'),
            style_cell={'padding' : '8px'}
        )
    ])
)

# ---------------------
# App layout

app.layout = dbc.Container(children=[

    dbc.Row([
        title_card
    ], 
    justify='center',
    style={
        'margin-top': 30,
        'margin-bottom': 30
    }),

    dbc.Row([
        dbc.Col(projection_card, width='auto'),
        dbc.Col(words_card, width='auto')
    ], justify='around', align='center'),

    dbc.Row([
        dbc.Col(author_card, width=300),
        dbc.Col(confidence_card, width='auto'),
    ], 
    justify='around',
    style={
        'margin-top': 30,
        'margin-bottom': 50
    }),

], fluid=True)

# ---------------------
# Interactivity
@app.callback(
    Output('words-table', 'data'),
    Input('genre-select', 'value')
)
def update_table(genre_selection):

    return(generateWordsTable(genre_selection, max_rows=15).to_dict('records'))

@app.callback(
    Output('confidence-fig', 'figure'),
    Input('title-select', 'value')
)
def update_confidence(title_selection):

    if title_selection:
        return(generateConfidenceFig(book_id=title_selection))
    else:
        raise PreventUpdate

@app.callback(
    Output('authors-table', 'data'),
    Input('author-select', 'value')
)
def update_author(author_selection):

    return(getAuthorTable(author_selection).to_dict('records'))

# ---------------------
# Run app
if __name__ == '__main__':
    app.run_server(debug=True)