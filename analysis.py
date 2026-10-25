from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display
# Resolve inputs relative to this script, regardless of the caller's directory.
ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'outputs'
OUT.mkdir(exist_ok=True)
pd.set_option('display.max_columns', 12)
pd.set_option('display.float_format', lambda value: f'{value:,.3f}')
plt.rcParams.update({'figure.figsize': (10, 5), 'font.size': 11,
                     'axes.spines.top': False, 'axes.spines.right': False})
BLUE = '#24577A'


source = ROOT / 'data' / 'imdb_movies.csv'
if not source.exists():
    raise FileNotFoundError(f'Missing original movie dataset: {source}')
raw = pd.read_csv(source)
required = ['original_title','genres','budget','revenue','popularity','vote_count','vote_average','release_year']
assert not (set(required)-set(raw)), 'Movie dataset schema differs from the submitted notebook'
movies = raw.drop_duplicates().copy()
key = 'id' if 'id' in movies else 'imdb_id' if 'imdb_id' in movies else None
if key is None: raise ValueError('A stable movie ID is required; titles are not unique identifiers')
assert movies[key].notna().all(), 'Investigate missing IDs'
assert not movies[key].duplicated().any(), 'Resolve conflicting movie IDs before analysis'
movies = movies.rename(columns={key:'movie_id'})
num = ['budget','revenue','popularity','vote_count','vote_average','release_year']
for col in num:
    converted = pd.to_numeric(movies[col],errors='coerce')
    assert not (movies[col].notna() & converted.isna()).any(), f'Invalid numeric values: {col}'
    movies[col] = converted
assert movies['vote_average'].dropna().between(0,10).all()
assert movies['vote_count'].dropna().ge(0).all()
valid_genre = movies['genres'].notna() & movies['genres'].fillna('').str.strip().ne('')
financial = movies['budget'].gt(0) & movies['revenue'].gt(0)
quality = pd.Series({'source_rows':len(raw),'exact_duplicates_removed':len(raw)-len(movies),
    'unique_movies':len(movies),'missing_genre_movies':int((~valid_genre).sum()),
    'usable_financial_movies':int(financial.sum())})
display(quality.to_frame('count'))
quality.to_csv(OUT/'quality_checks.csv')
movies['gross_surplus_proxy'] = (movies['revenue']-movies['budget']).where(financial)
movies['reported_budget'] = movies['budget'].where(financial)
movies['reported_revenue'] = movies['revenue'].where(financial)


genres = movies.loc[valid_genre].copy()
genres['genre'] = genres['genres'].str.split('|')
genres = genres.explode('genre')
genres['genre'] = genres['genre'].str.strip()
genres = genres.loc[genres['genre'].ne('')].drop_duplicates(['movie_id','genre'])
genre_summary = genres.groupby('genre').agg(
    movies=('movie_id','nunique'), mean_popularity=('popularity','mean'),
    financial_movies=('gross_surplus_proxy','count'), mean_budget=('reported_budget','mean'),
    median_budget=('reported_budget','median'), mean_revenue=('reported_revenue','mean'),
    median_revenue=('reported_revenue','median'), median_surplus=('gross_surplus_proxy','median'))
display(genre_summary.sort_values('movies',ascending=False))
genre_summary.to_csv(OUT/'genre_summary.csv')
fig,ax=plt.subplots(figsize=(10,7))
genre_summary['movies'].sort_values().plot.barh(ax=ax,color=BLUE)
ax.set(title='Movies by genre (memberships overlap)',xlabel='Unique movie IDs',ylabel='')
fig.tight_layout();fig.savefig(OUT/'genre_counts.png',dpi=160,bbox_inches='tight');plt.show()


fig,axes=plt.subplots(1,2,figsize=(13,7))
genre_summary[['mean_budget','mean_revenue']].sort_values('mean_budget').plot.barh(ax=axes[0],color=[BLUE,'#D69B32'])
axes[0].set(title='Mean reported financial amounts',xlabel='Source monetary units; positive budget and revenue',ylabel='')
genre_summary['mean_popularity'].sort_values().plot.barh(ax=axes[1],color=BLUE)
axes[1].set(title='Mean popularity by genre',xlabel='Source popularity score',ylabel='')
fig.tight_layout();fig.savefig(OUT/'genre_finance_popularity.png',dpi=160,bbox_inches='tight');plt.show()


MIN_VOTES=50
qualified = genres.loc[genres['vote_count'].ge(MIN_VOTES) & genres['vote_average'].notna()]
eligible = qualified.groupby('genre')['movie_id'].nunique()
high = qualified.loc[qualified['vote_average'].ge(8)].groupby('genre')['movie_id'].nunique()
ratings = eligible.rename('eligible_movies').to_frame()
ratings['high_rated_movies'] = high.reindex(ratings.index,fill_value=0)
ratings['high_rating_rate'] = ratings['high_rated_movies']/ratings['eligible_movies']
assert ratings['high_rated_movies'].le(ratings['eligible_movies']).all()
display(ratings.sort_values('high_rated_movies',ascending=False))
ratings.to_csv(OUT/'high_rating_summary.csv')
fig,ax=plt.subplots(figsize=(10,7))
ratings['high_rated_movies'].sort_values().plot.barh(ax=ax,color=BLUE)
ax.set(title='Movies rated at least 8 with at least 50 votes',xlabel='Unique movie IDs',ylabel='')
fig.tight_layout();fig.savefig(OUT/'high_rating_counts.png',dpi=160,bbox_inches='tight');plt.show()


selected = movies.loc[financial & movies['vote_count'].ge(MIN_VOTES)]
pairs=[('vote_average','revenue'),('vote_average','gross_surplus_proxy'),
       ('popularity','revenue'),('popularity','gross_surplus_proxy'),
       ('budget','revenue'),('budget','gross_surplus_proxy'),('budget','popularity')]
associations=[]
for x,y in pairs:
    sample=selected[[x,y]].dropna()
    rho=sample[x].corr(sample[y],method='spearman') if len(sample)>1 and sample[x].nunique()>1 and sample[y].nunique()>1 else np.nan
    associations.append({'x':x,'y':y,'n':len(sample),'spearman_rho':rho})
associations=pd.DataFrame(associations)
display(associations)
associations.to_csv(OUT/'associations.csv',index=False)
fig,ax=plt.subplots(figsize=(8,5))
ax.scatter(selected['budget'],selected['revenue'],s=12,alpha=.3,color=BLUE)
ax.set(xscale='log',yscale='log',xlabel='Reported budget (log scale)',ylabel='Reported revenue (log scale)',title='Budget and revenue • one point per eligible movie')
fig.tight_layout();fig.savefig(OUT/'budget_revenue.png',dpi=160,bbox_inches='tight');plt.show()


import seaborn as sns
year_stats=genres.groupby(['genre','release_year']).agg(n=('gross_surplus_proxy','count'),median_surplus=('gross_surplus_proxy','median'))
year_stats['median_surplus']=year_stats['median_surplus'].where(year_stats['n'].ge(5))
year_stats.to_csv(OUT/'genre_year_financials.csv')
matrix=year_stats['median_surplus'].unstack()
if matrix.notna().any().any():
    fig,ax=plt.subplots(figsize=(16,8))
    sns.heatmap(matrix,ax=ax,cmap='RdBu',center=0,cbar_kws={'label':'Median reported gross surplus proxy'})
    ax.set(title='Genre/year cells with at least five financial observations',xlabel='Release year',ylabel='Genre')
    fig.tight_layout();fig.savefig(OUT/'genre_year.png',dpi=160,bbox_inches='tight');plt.show()
