# ## Import statements and matplotlib configs

# In[1]:

import matplotlib.pyplot as plt
import missingno as msno
import numpy as np
import pandas as pd
import requests

# `pd.__version__` must be at least 0.25.0 to run the [explode()](https://pandas.pydata.org/pandas-docs/version/0.25/user_guide/reshaping.html#exploding-a-list-like-column) functions.
#
# If not, run `!pip install pandas --upgrade`.

# In[2]:

pd.__version__

# In[3]:

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)
pd.set_option('plotting.backend', 'matplotlib')
pd.options.display.float_format = '{:.2f}'.format

get_ipython().run_line_magic('matplotlib', 'inline')
plt.style.use('fivethirtyeight')

get_ipython().run_line_magic('config', "InlineBackend.figure_format ='retina'")

# ## Global variables and dataframes

# In[4]:

GREEN = '#4BF03F'
YELLOW = '#FCE312'
ORANGE = '#FDA44E'
PINK = '#E266FD'
VIOLET = '#5A1EFD'
BROWN = '#1F0E1C'
SKYBLUE = '#61ECF0'
WHITE = '#F0F0F0'
RED = '#F03939'

# In[42]:

# Initalise global data frames
books = pd.DataFrame()
movies = pd.DataFrame()
books_s1 = pd.DataFrame()
movies_s1 = pd.DataFrame()

books_ex = pd.DataFrame()
movies_ex = pd.DataFrame()
merge_ex = pd.DataFrame()

books_ex_save = pd.DataFrame()
movies_ex_save = pd.DataFrame()
merge_ex_save = pd.DataFrame()

initial_books, initial_movies = 0, 0
df_status = {}
error_log = []

# ## Helper functions

# In[43]:

def get_shapes():
    """
    Updates df_status and returns the dictionary.
    """

    global df_status

    df_status = {'books': books.shape,
                 'books_s1': books_s1.shape,
                 'movies': movies.shape,
                 'movies_s1': movies_s1.shape,
                 'books_ex': books_ex.shape,
                 'books_ex_save': books_ex_save.shape,
                 'movies_ex': movies_ex.shape,
                 'movies_ex_save': movies_ex_save.shape,
                 'merge_ex': merge_ex.shape,
                 'merge_ex_save': merge_ex_save.shape,
                 'initial_books': initial_books,
                 'initial_movies': initial_movies}

    return df_status

# In[44]:

def save(get_shape=False):
    """
    Saves current state of data frames for easy access. 
    Run before methods that critically update dataframes.

    Args: 
        get_shape: (default: False) returns get_shape() if True.
    """

    global books_s1
    global movies_s1
    global books_ex_save
    global movies_ex_save
    global merge_ex_save

    books_s1 = books.copy(deep=True)
    movies_s1 = movies.copy(deep=True)

    books_ex_save = books_ex.copy(deep=True)
    movies_ex_save = movies_ex.copy(deep=True)
    merge_ex_save = merge_ex.copy(deep=True)

    print('\nDataframes saved.')
    if get_shape:
        return get_shapes()

def restore(get_shape=False):
    """
    Restores data frames from last save state.

    Args: 
        get_shape: (default: False) returns get_shape() if True.
    """

    global books
    global movies
    global books_ex
    global movies_ex
    global merge_ex

    books = books_s1.copy(deep=True)
    movies = movies_s1.copy(deep=True)

    books_ex = books_ex_save.copy(deep=True)
    movies_ex = movies_ex_save.copy(deep=True)
    merge_ex = merge_ex_save.copy(deep=True)

    print('\nDataframes recovered.')
    if get_shape:
        return get_shapes()

# In[45]:

def read_data():
    """
    Reads from csv files.
    """

    global books
    global movies
    global initial_books
    global initial_movies

    books = pd.read_csv('data/books.csv')
    movies = pd.read_csv('data/movies.csv')

    books = books.round(4)
    movies = movies.round(4)

    initial_books = books.shape
    initial_movies = movies.shape

    print("'books.csv' and 'movies.csv' have been read with shapes: {} and {}".format(
        books.shape, movies.shape))

# In[46]:

def lowercase_dfs():
    """
    Converts columns to str and changes them to lowercase.
    """

    global books
    global movies

    global error_log
    local_errors = 0

    nan_to_string = ['author', 'title']

    for col_name in nan_to_string:
        try:
            books[col_name][books[col_name].isnull()] = ''
            movies[col_name][movies[col_name].isnull()] = ''
        except KeyError as e:
            error_log.append({'lowercase_dfs()': e})
            local_errors += 1
            pass

    books = books.applymap(lambda c: c.lower().strip()
                           if type(c) == str else c)
    movies = movies.applymap(lambda c: c.lower().strip()
                             if type(c) == str else c)

    print('\nDataframes lowercased with {} errors.'.format(local_errors))

# In[47]:

def clean_dates():
    """
    Convert str dates to datetime objects.
    """

    global error_log
    local_errors = 0

    try:
        books['gc_text_reviews_count'] = books['gc_text_reviews_count'] + 1
        books['publish_date'] = pd.to_datetime(books['publish_date'])
        books['publish_year'] = books['publish_date'].dt.year

        movies['imdb_released'] = pd.to_datetime(movies['imdb_released'])
    except ValueError or AttributeError as e:
        error_log.append({'clean_dates() --> to_datetime': e})
        local_errors += 1
        pass

    try:
        books.drop(columns=['book_wiki_url', 'adaptations',
                            'title', 'gc_title'], inplace=True)
    except KeyError as e:
        error_log.append({'clean_dates() --> drop cols': e})
        local_errors += 1
        pass

    movies['imdb_year'] = movies['imdb_year'].str[:4]
    movies['imdb_year'] = movies['imdb_year'].astype('float')

    try:
        movies['imdb_runtime'] = movies['imdb_runtime'].str[:-4]
        movies['imdb_runtime'] = movies['imdb_runtime'].astype('float')
    except ValueError:
        pass

    print('\nDates cleaned with {} errors.'.format(local_errors))

# In[48]:

def merge_rows():
    """
    Merges non unique rows.
    """

    global books
    global movies

    books = books.groupby(['book_id']).agg('max').reset_index()
    movies = movies.groupby(['movie_id']).agg('max').reset_index()
    print("\nRows merged by book_id and movie_id with shapes: {} and {}".format(
        books.shape, movies.shape))

# In[49]:

def str_to_list(df, list_of_columns):
    """
    Runs list_clean() for a list of columns in a particular dataframe. 
    """
    for col in list_of_columns:
        df[col] = df[col].apply(list_clean, convert_dtype=True)

    print('\n', list_of_columns, 'is cleaned.')

def list_clean(str_list):
    """
    Converts a list in str form to a list seperated by ','.
    """

    str_list = str(str_list)
    cleaned_list = str_list.replace("'", '').replace(
        '[', '').replace(']', '').replace('"', '')
    cleaned_list = [element.strip() for element in cleaned_list.split(',')]

    if len(cleaned_list) == 1:
        if 'nan' in cleaned_list:
            cleaned_list = None
        else:
            cleaned_list = cleaned_list[0]

    return cleaned_list

list_clean("['secret service', 'world war, 1939-1945', 'fiction']")

# In[50]:

def get_missing_authors():
    """
    Fixes some missing authors.
    """

    missing_author = list(books['isbn'].loc[books['author'] == ''])
    fix = False
    for isbn in missing_author:
        curl = 'https://openlibrary.org/api/books?bibkeys=ISBN:{}&jscmd=data&format=json'.format(
            isbn)
        all_metadata = requests.get(curl).json()
        try:
            author = all_metadata['ISBN:{}'.format(isbn)]['authors'][0]['name']
            books['author'].loc[books['isbn'] == isbn] = author
            print(author)
            fix = True
        except KeyError:
            pass
    if fix:
        print('\nSome missing authors have been restored.')

# In[51]:

def real_prices():
    """
    Converts box office returns/budgets to 2010 dollars to account for inflation.
    """

    global movies

    t_inflation = pd.read_csv('data/ticket_inflation.csv')
    g_inflation = pd.read_csv('data/general_inflation.csv')
    g_inflation = g_inflation.astype(float)
    t_inflation = t_inflation.astype(float)
    g_inflation = g_inflation.merge(t_inflation, on='imdb_year')

    movies = movies.merge(g_inflation, on='imdb_year')

    for col in ['opening_weekend_usa', 'gross_usa']:
        movies[col + '_2010_dollars'] = movies[col] / \
            movies['ticket_inflation_rate']
    movies['budget_2010_dollars'] = movies['budget'] / \
        movies['general_inflation_rate']

    print('Prices converted to 2010 dollars.')

# In[52]:

def get_dtype_summary(df):
    """
    Augmented data type summary.
    """

    w = pd.DataFrame(df.dtypes, columns=['dtype']).rename_axis('keys')
    x = pd.DataFrame(df.isnull().sum(), columns=[
                     'null_count']).rename_axis('keys')
    y = pd.DataFrame(df.isnull().sum()/len(df),
                     columns=['null_percent']).rename_axis('keys')
    z = pd.DataFrame(df.count(), columns=[
                     'non_null_count']).rename_axis('keys')
    w = w.merge(x.merge(y.merge(z, on='keys'), on='keys'), on='keys')
    print(w)

# ## Loading data and preprocessing

# In[53]:

error_log = []
read_data()
get_missing_authors()
lowercase_dfs()
merge_rows()

str_to_list(books, ['subjects', 'subject_places', 'publish_places'])
str_to_list(movies, ['imdb_actors', 'imdb_writers', 'imdb_genres'])

clean_dates()
real_prices()

save(True)

# ## Exploring dataframe `dtypes` and dropping NaNs

# In[54]:

books.columns

# In[55]:

books.describe()

# In[56]:

get_dtype_summary(books)

# In[57]:

get_dtype_summary(movies)

# ### Dropping columns values

# In[58]:

books.drop(columns=['gc_authors', 'count', 'goodreads'], inplace=True)
movies = movies.loc[movies['imdb_runtime'].astype(str).str.isnumeric()]
movies['imdb_runtime'] = movies['imdb_runtime'].astype(int)
save(True)

# ## EDA

# ### Exploring the books dataframe

# In[59]:

top_authors = books['author'].value_counts()[1:20]
plt.figure(figsize=(20, 4))
plt.bar(x=top_authors.index, height=top_authors.values, label='book count')
plt.xticks(rotation=90)
plt.ylabel('number of books in the dataset')
plt.ylim([0, 13])
plt.axhline(np.nanmean(books['author'].value_counts()),
            label='sample mean', c=YELLOW, xmin=.04, xmax=.96)
plt.axhline(np.nanmedian(books['author'].value_counts(
)), label='sample median', c=PINK, xmin=.04, xmax=.96)
plt.legend()
plt.title('Most popular authors')
plt.show()

# In[60]:

plt.figure(figsize=(20, 4))

plt.axvline(x=np.nanmean(books['publish_year']), c=YELLOW, label='sample mean')
plt.axvline(x=np.nanmedian(books['publish_year']),
            c=PINK, label='sample median')
plt.axvline(x=1965, c=GREEN, label="'New Hollywood' era begins")
plt.hist(x=books['publish_year'], bins=100, label='book count')
plt.ylim([0, 40])
plt.xticks(ticks=range(1840, 2030, 10))
plt.xlabel('publishing year')
plt.ylabel('# of books in the dataset')
plt.title('Distribution of publishing year', pad=5)
plt.legend()
plt.show()

# In[61]:

plt.figure(figsize=(10, 4))

plt.axvline(x=np.nanmean(books['gc_average_rating']),
            c=YELLOW, label='sample mean')
plt.axvline(x=np.nanmedian(
    books['gc_average_rating']), c=PINK, label='sample median')
plt.hist(x=books['gc_average_rating'], bins=20, label='book count')
plt.xlabel('average ratings')
plt.ylabel('number of books')
plt.xlim([3, 5])
plt.title('Distribution of book ratings (on goodreads)', pad=5)
plt.legend(fontsize='small')
plt.show()

# In[62]:

good_books = books.loc[books['gc_average_rating'] > 4]
meh_books = books.loc[books['gc_average_rating'] <= 4]

plt.figure(figsize=(20, 5))
plt.hist(x=meh_books['number_of_pages'],
         bins=75, label='page count for books rated 4.0 or less', alpha=0.5)
plt.hist(x=good_books['number_of_pages'], bins=75,
         label='page count for books rated 4.0 or more', color=ORANGE, alpha=0.5)
plt.xlabel('number of pages')
plt.ylabel('# of books in the dataset')
plt.axvline(x=np.nanmedian(meh_books['number_of_pages']),
            label='sample median for books rated 4.0 and less')
plt.axvline(x=np.nanmedian(good_books['number_of_pages']),
            c=ORANGE, label='sample median for books rated 4.0 and more')
plt.title('Distribution of number of pages', pad=5)
plt.xticks(range(0, 1200, 100))
plt.legend()
plt.show()

# In[63]:

subjects = books.explode('subjects')
vc = subjects['subjects'].value_counts() > 10
vc_true = [s for s in vc.index if vc[s] != False]
subjects = subjects.loc[subjects['subjects'].isin(vc_true)]
x = subjects.groupby(by='subjects')[
    'gc_average_rating', 'publish_year'].median()
x.sort_values(by='gc_average_rating', ascending=False)[
    :10], x.sort_values(by='gc_average_rating', ascending=True)[:10]

# ### Exploring the movie dataframe

# In[64]:

movies.columns

# In[65]:

movies.describe()

# In[66]:

top_movies = movies.loc[movies['imdb_imdbrating'] >= 8]
meh_movies = movies.loc[movies['imdb_imdbrating'] < 8]

# In[67]:

plt.figure(figsize=(12, 4))

plt.axvline(x=np.nanmean(movies['imdb_imdbrating']),
            c=YELLOW, label='sample mean')
plt.axvline(x=np.nanmedian(
    movies['imdb_imdbrating']), c=PINK, label='sample median')
plt.hist(x=movies['imdb_imdbrating'], bins=25, label='movie count')
plt.xlabel('average ratings')
plt.ylabel('number of movies')
plt.xticks(np.arange(0, 10, 0.5))
plt.title('Distribution of movie IMDb ratings')
plt.legend(fontsize='small')
plt.show()

# In[68]:

plt.figure(figsize=(12, 4))

plt.axvline(x=np.nanmean(movies['imdb_runtime']), c=YELLOW,
            label='sample mean: {} mins'.format(np.nanmean(movies['imdb_runtime'])))
plt.axvline(x=np.nanmedian(movies['imdb_runtime']), c=PINK, label='sample median: {} mins'.format(
    np.nanmedian(movies['imdb_runtime'])))
plt.hist(x=movies['imdb_runtime'], bins=45, label='movie count')
plt.xlabel('runtime (in mins)')
plt.ylabel('number of movies')
plt.xticks(ticks=range(0, 400, 20))
plt.title('Distribution of movie runtimes (IMDb data)')
plt.legend(fontsize='small')
plt.show()

# In[69]:

g1 = plt.figure(figsize=(9, 5))
plt.scatter(x=top_movies['imdb_runtime'], y=(top_movies['imdb_imdbrating']),
            label='IMDb ratings (top rated movies)', alpha=0.4)
plt.scatter(x=meh_movies['imdb_runtime'], y=(meh_movies['imdb_imdbrating']),
            label='IMDb ratings (meh rated movies)', alpha=0.4, color=ORANGE)
plt.axvline(x=np.median(top_movies['imdb_runtime']),
            label='median runtime for movies rated 8.0 or more', lw=2.5)
plt.axvline(x=np.median(meh_movies['imdb_runtime']),
            label='median runtime for movies rated 8.0 or less', color=ORANGE, lw=2.5)

plt.ylabel('IMDb ratings')
plt.xlabel('runtime (in minutes)')
plt.title('Comparing median runtimes between top-rated and non-rated movies')
plt.xticks(range(0, 400, 30))
plt.legend(fontsize='small')
plt.show()

# In[70]:

actors = movies.explode('imdb_actors')
actors = actors[['movie_title', 'imdb_actors', 'imdb_year',
                 'imdb_imdbrating', 'gross_usa_2010_dollars', 'cumulative_worldwide_gross']]
actors.dropna(subset=['movie_title', 'imdb_actors',
                      'imdb_imdbrating', 'gross_usa_2010_dollars'], inplace=True)

vc = actors['imdb_actors'].value_counts() > 2
vc_true = [a for a in vc.index if vc[a] != False]
actors = actors.loc[actors['imdb_actors'].isin(vc_true)]
x = actors.groupby(by='imdb_actors').mean()

# In[71]:

def actor_profile(name):
    """
    Returns movies for any given actor.
    """

    return actors[['movie_title', 'imdb_year', 'imdb_actors', 'imdb_imdbrating', 'gross_usa_2010_dollars']
                  ].loc[actors['imdb_actors'] == name]

name = 'daniel radcliffe'
actor_profile(name)

# In[72]:

x.sort_values(by='gross_usa_2010_dollars', ascending=False)[:10]

# no deathly hallows

# In[73]:

x.sort_values(by='imdb_imdbrating', ascending=False)[:10]

# In[74]:

x.sort_values(by='imdb_imdbrating', ascending=True)[:5]

# just goes to show that series deals are bad deals

# In[75]:

plt.figure(figsize=(9, 5))
plt.scatter(x=movies['imdb_year'], y=(movies['budget']),
            label='budget', c=RED, alpha=0.5)
plt.scatter(x=movies['imdb_year'], y=(
    movies['gross_usa']), label='american sales', alpha=0.5)
plt.scatter(x=movies['imdb_year'], y=(movies['cumulative_worldwide_gross']),
            label='global sales', alpha=0.5, c=GREEN)
plt.title('Growth of movie sales and expenses (nominal dollars)')
plt.yticks(np.arange(0, 1200000000, 100000000), labels=range(0, 12))
plt.ylabel("100,000 USD (nominal numbers)")
plt.xlabel('year')
plt.legend(fontsize='small')
plt.show()

# In[76]:

plt.figure(figsize=(9, 5))
plt.scatter(x=movies['imdb_year'], y=(movies['budget_2010_dollars']),
            label='production budget (in 2010 dollars)', c=RED, alpha=0.5)
plt.scatter(x=movies['imdb_year'], y=(
    movies['gross_usa_2010_dollars']), label='american sales (in 2010 dollars)', alpha=0.5)
plt.title('Growth of movie sales and expenses (2010 dollars)')
plt.yticks(np.arange(0, 1000000000, 100000000), labels=range(0, 12))
plt.ylabel("$100 mil (2010 dollars)")
plt.xlabel('year')
plt.legend(fontsize='small')
plt.show()

# In[77]:

plt.figure(figsize=(10, 5))
plt.scatter(x=top_movies['imdb_imdbrating'], y=(top_movies['gross_usa_2010_dollars']),
            label='gross USA sales (2010 dollars) for top movies', c=RED, alpha=0.5)
plt.scatter(x=meh_movies['imdb_imdbrating'], y=(
    meh_movies['gross_usa_2010_dollars']), label='gross USA sales (2010 dollars) for meh movies', alpha=0.5)
plt.yticks(np.arange(0, 1000000000, 100000000), labels=range(0, 12))
plt.ylabel("$100 mil (2010 dollars)")
plt.title('Growth of movie sales and expenses (2010 dollars)')
plt.xlabel('IMDB rating')
plt.xticks(np.arange(3.5, 10, 0.5))
plt.legend(fontsize='small')
plt.show()

# In[78]:

genres = movies.explode('imdb_genres')
genres = genres[['movie_title', 'imdb_genres', 'imdb_year',
                 'imdb_imdbrating', 'gross_usa_2010_dollars', 'cumulative_worldwide_gross']]
genres.dropna(inplace=True, subset=['movie_title', 'imdb_genres', 'imdb_year',
                                    'imdb_imdbrating', 'gross_usa_2010_dollars'])

# In[79]:

plt.figure(figsize=(18, 5))
for g in genres['imdb_genres'].value_counts()[:5].index:
    g_select = genres.loc[genres['imdb_genres'] == g]
    vc = g_select['imdb_year'].value_counts(dropna=True).sort_index()
    x = list(vc.index)
    y = list(vc.values)
    plt.plot(x, y, '--*', lw=1.5, label=g)

plt.ylabel('numbers of films for given genre in a year', fontsize='small')
plt.xlabel('year')
plt.yticks(range(1, 10))
plt.xticks(range(1950, 2020, 4))
plt.legend(loc=4, bbox_to_anchor=(1.1, 0))
plt.title('yearly growth of the top 5 most popular movie genres')
plt.show()

# In[80]:

t_genres = genres.loc[genres['imdb_imdbrating'] >= 8]
m_genres = genres.loc[genres['imdb_imdbrating'] < 8]

plt.figure(figsize=(10, 8))

for g in genres['imdb_genres'].unique():
    m_g_select = m_genres.loc[m_genres['imdb_genres'] == g]
    plt.scatter(y=m_g_select['imdb_genres'],
                x=m_g_select['gross_usa_2010_dollars'], color=ORANGE, alpha=0.5)

    t_g_select = t_genres.loc[t_genres['imdb_genres'] == g]
    plt.scatter(y=t_g_select['imdb_genres'],
                x=t_g_select['gross_usa_2010_dollars'], color=VIOLET, marker='*')

plt.xticks(np.arange(0, 900000000, 100000000), labels=range(0, 12))
plt.xlabel("$100 mil (in 2010 dollars)")
plt.title('US box office earnings by genre (top rated movies are ★)')
plt.show()

# In[81]:

vc = genres['imdb_genres'].value_counts() > 5
vc_true = [g for g in vc.index if vc[g] != False]
genres_2 = genres.loc[genres['imdb_genres'].isin(vc_true)]
x = genres_2.groupby(by='imdb_genres').median()

x.sort_values(by='imdb_imdbrating', ascending=False)[:5]

# In[82]:

x.sort_values(by='gross_usa_2010_dollars', ascending=False)[:5]

# x.sort_values(by = 'cumulative_worldwide_gross', ascending = False)[:5]

# ## Finding patterns across adaptations

# ### Merging `books` and `movies` on `book_id`

# In[83]:

merged = movies.merge(books, on='book_id')
merged.dropna(subset=['imdb_imdbrating', 'gc_average_rating',
                      'gross_usa_2010_dollars'], inplace=True)
merged['time_between_book_and_movie'] = merged['imdb_year'] - \
    merged['publish_year']
merged['time_between_book_and_movie'].loc[merged['time_between_book_and_movie'] < 0] = -1

# ### Defining the `must_see_index`

# In[84]:

merged['must_see_index'] = ((merged['imdb_imdbrating'] ** 2 /
                             merged['gc_average_rating']) * (np.log(merged['imdb_runtime']) ** 2))

eighty_percentile = round(np.percentile(merged['must_see_index'], 80), 3)

plt.figure(figsize=(10, 5))
plt.hist(x=merged['must_see_index'], bins=20)
plt.axvline(x=np.median(merged['must_see_index']),
            label='median must_see_index value', color=PINK)
plt.axvline(x=eighty_percentile, label='eighty percentile cut off for must_see ({})'.format(
    eighty_percentile), color=ORANGE)
#plt.xticks(ticks = range(0, 110, 20))
plt.yticks(ticks=range(0, 16, 2))
plt.xlabel('must_see_index for the adaptation')
plt.ylabel('% of values')
plt.legend(fontsize='small')
plt.title("Distribution of 'must_see_index' values")
plt.show()

# In[85]:

merged['must_see_index'].describe()

# In[86]:

merged['must_see'] = merged['must_see_index'].apply(
    lambda x: True if x > eighty_percentile else False)
merged['must_see'].value_counts()

# In[87]:

merged_important = ['movie_title', 'book_title_x', 'imdb_year', 'must_see_index', 'must_see',
                    'imdb_imdbrating', 'gc_average_rating', 'gross_usa_2010_dollars', 'imdb_runtime',
                    'cumulative_worldwide_gross']

# ### Splitting merged dataframes into `must_see_rated` and `not_must_see_rated` with 80th percentile of `must_see_index` as cutoff

# In[88]:

must_see_rated = merged.query('must_see == True')
not_must_see_rated = merged.query('must_see == False')

must_see_rated.shape, not_must_see_rated.shape

# Incorporating "not as good as the book factor"

# In[89]:

plt.figure(figsize=(13, 5))
plt.scatter(x=must_see_rated['gc_average_rating'], y=must_see_rated['imdb_imdbrating'],
            color=ORANGE, label='top rated adaptations')
plt.scatter(x=not_must_see_rated['gc_average_rating'],
            y=not_must_see_rated['imdb_imdbrating'], label='meh rated adaptations')

plt.axvline(x=np.percentile(merged['gc_average_rating'], 80),
            color=PINK, lw=2.5, label='80 percentile of goodreads rating')
plt.axhline(y=np.percentile(merged['imdb_imdbrating'], 80),
            color=GREEN, lw=2.5, label='80 percentile of imdb rating')

plt.title('IMDb ratings vs Goodreads ratings')

plt.xlabel('Goodreads rating')
plt.xlim([3.25, 4.75])
plt.ylabel('IMDb rating')
plt.legend(fontsize='small')
plt.show()

# In[90]:

plt.figure(figsize=(14, 5))
plt.scatter(x=must_see_rated['gc_average_rating'], y=must_see_rated['must_see_index'],
            color=ORANGE, label='top rated adaptations')
plt.scatter(x=not_must_see_rated['gc_average_rating'],
            y=not_must_see_rated['must_see_index'], label='meh rated adaptations')
plt.title('IMDb ratings vs Goodreads ratings')

plt.axvline(x=np.percentile(merged['gc_average_rating'], 80),
            color=PINK, lw=2.5, label='80 percentile of goodreads rating')
plt.axhline(y=np.percentile(merged['must_see_index'], 80),
            color=GREEN, lw=2.5, label='80 percentile of imdb rating')

plt.xlabel('goodreads rating')
plt.xlim([3.25, 4.75])
plt.ylabel('must_see_index')
plt.legend(fontsize='small')
plt.show()

# In[91]:

merged.columns

# ### Exploring correlations between various movie variables

# In[92]:

merged[['must_see_index', 'imdb_imdbrating', 'gc_average_rating', 'imdb_runtime', 'gross_usa_2010_dollars',
        'cumulative_worldwide_gross']].corr()

# ## Final list of must see movies

# In[93]:

merged[merged_important].loc[merged['must_see'] == True].sort_values(
    by='must_see_index', ascending=False)
