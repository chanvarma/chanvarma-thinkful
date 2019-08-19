# ## Import statements and API keys

# In[19]:

from imdb import IMDb  # For adding book related metadata
import socket
# For error handling while working with links
from xml.parsers.expat import ExpatError
from xml.parsers.expat import ExpatError
from socket import gaierror
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import re
import copy  # For deep copying dicts to create 'save points'

from goodreads import client  # For adding book related metadata
gc = client.GoodreadsClient('9addHIFaPJmit7dzC5ZA',
                            'iDXvx13Rnt1iJkWOxRkSh9wLnbFWmMNgCUMFLJmLPo')

OMBD_API_KEY = '2cb213a7'

# In[155]:

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)

# ## Information sources

# In[20]:

wikipages = ['https://en.wikipedia.org/wiki/List_of_children%27s_books_made_into_feature_films?oldformat=true',
             'https://en.wikipedia.org/wiki/List_of_fiction_works_made_into_feature_films_(0%E2%80%939,_A%E2%80%93C)?oldformat=true',
             'https://en.wikipedia.org/wiki/List_of_fiction_works_made_into_feature_films_(D%E2%80%93J)?oldformat=true',
             'https://en.wikipedia.org/wiki/List_of_fiction_works_made_into_feature_films_(K%E2%80%93R)?oldformat=true',
             'https://en.wikipedia.org/wiki/List_of_fiction_works_made_into_feature_films_(S%E2%80%93Z)?oldformat=true'
             ]

# In[21]:

imdb_lists = ['https://www.imdb.com/list/ls000989358/',  # 2011 list: 71 movies
              'https://www.imdb.com/list/ls000004341/',  # 2010 list: 20 movies
              'https://www.imdb.com/list/ls070762787/',  # 2014 list: 20 movies
              'https://www.imdb.com/list/ls029848347/',  # 2019 list: 23 movies
              'https://www.imdb.com/list/ls053974803/',  # 2013 list: 23 movies
              'https://www.imdb.com/list/ls076239083/',  # 2015 list: 10 movies
              'https://www.imdb.com/list/ls000420337/?sort=user_rating,desc&st_dt=&mode=detail&page=1',
              # 2011 list: 100 movies, sorted by IMDb ratings (desc)
              'https://www.imdb.com/list/ls000099866/?sort=runtime,desc&st_dt=&mode=detail&page=1',
              # 2011 list: 100 movies, sorted by Runtime (desc)
              ]

# ## Helper functions

# In[23]:

def working_wiki_link(wiki_link):
    """
    Converts relative URLs to global URLs.
    """
    if 'fr.wiki' in wiki_link or 'ru.wiki' in wiki_link:
        return ''

    if '/wiki/' in wiki_link:
        return 'https://en.wikipedia.org' + wiki_link
    return wiki_link

# In[24]:

def get_adaptations(book_title, href_list, isbn_oclc):
    """
    Parses through list of movies associated with a specific `book_title`,
    adds movies to `movie_book_dict`, and returns list of movies.
    Adds year to the movie title if information available.

    Args:
        book_title: (str) name of original book.
        href_list: (list) Result of findAll('a') on the movies column.
        isbn_oclc: (dict) ISBN and OCLC numbers to pass on to movie.

    Returns:
        adaptations: List of movie title names.
    """
    adaptations = []

    if len(href_list) == 1:
        adaptations.append(href_list[0]['title'])
        return adaptations

    for index, tag in enumerate(href_list):
        year_search = re.search(r'\d\d\d\d', tag['href'])

        if year_search is not None:  # There is a 4 digit number in the title
            year_search = year_search.group()

            if year_search not in tag['title']:
                version = tag['title'] + ' (' + year_search + ')'
            else:
                version = tag['title']

            adaptations.append(version)

        else:
            version = tag['title']
            adaptations.append(version)

        try:
            isbn = isbn_oclc['isbn']
            oclc = isbn_oclc['oclc']
        except Exception:
            isbn = 'broken'
            oclc = 'broken'

        movie_book_dict[working_wiki_link(tag['href'])] = {'movie_title': version,
                                                           'book_title': book_title,
                                                           'imdb_no': '', 'usable': '',
                                                           'isbn': isbn, 'oclc': oclc}

    return adaptations

# In[25]:

def clean_adaptations(adaptations):
    """
    Makes sure the list of adaptations doesn't contain TV series or miniseries.
    """

    cleaned = []

    for title in adaptations:
        if 'TV' in title or 'miniseries' in title:
            continue
        elif 'page does not exist' in title:
            continue
        elif 'fr.wiki' or 'ru.wiki' in title:
            continue
        else:
            cleaned.append(title)

    return cleaned

# In[26]:

def add_to_book_film_dict():
    """
    Method parses newly updated rows for book/film title, book author,
    number of adaptions, and list of adaptations, and adds them to the
    `book_film_dict` as a nested dictionary.
    global sum_adaptations
    """
    global sum_adaptations

    for row in rows:
        cols = row.findAll('td')

        try:
            if (len(cols[0].findAll('a')) == 2) and (cols[1].find('a') is not None):
                series = cols[0].text.replace('\n', '').split(',')[0]

                book_title = cols[0].findAll('a')[0]['title']
                author = cols[0].findAll('a')[-1]['title']

                book_wiki_url = working_wiki_link(
                    cols[0].findAll('a')[0]['href'])

                try:
                    isbn_oclc = get_isbn_oclc(book_wiki_url)
                    isbn = isbn_oclc['isbn']
                    oclc = isbn_oclc['oclc']
                except TypeError or KeyError:
                    isbn = 'broken'
                    oclc = 'broken'

                try:
                    adaptations = clean_adaptations(get_adaptations(
                        book_title, cols[1].findAll('a'), isbn_oclc))
                except KeyError or TypeError:
                    adaptations = []
                    pass

                sum_adaptations += len(adaptations)

                if (isbn == 'broken' and oclc == 'broken'):
                    print('{} by {} 𝙓'.format(book_title, author))
                else:
                    print('{} by {} ✔️'.format(book_title, author))

                book_movie_dict_all[series] = {'author': author,
                                               'book_title': book_title,
                                               'book_wiki_url': book_wiki_url,
                                               'count': len(adaptations),
                                               'adaptations': adaptations,
                                               'isbn': isbn, 'oclc': oclc, 'valid_identifier': ''}

        except IndexError or KeyError:
            pass

    print("No. of rows/original books in dict: {}, No. of adaptations: {} \n"
          .format(len(book_movie_dict_all), sum_adaptations))

# In[235]:

def add_valid_books_to_dict():
    """
    Adds rows from `book_movie_dict_all` to `book_movie_dict'
    if they return a valid output for get_isbn_oclc().
    """
    global usable_count
    global broken_count

    for index, key in enumerate(book_movie_dict_all.keys()):
        link = book_movie_dict_all[key]['book_wiki_url']

        try:
            if book_movie_dict_all[key]['isbn'] == 'broken' and book_movie_dict_all[key]['oclc'] == 'broken':
                book_movie_dict_all[key]['valid_identifier'] = False
                # Nothing changes, the book is unusable, and the 'usable' flag remains False
            else:
                book_movie_dict_all[key]['valid_identifier'] = True
                # Deepcopy 'true' values to another dictionary
                book_movie_dict[key] = copy.deepcopy(book_movie_dict_all[key])
                usable_count += 1
        except NameError:
            pass

        if (index % 100 == 0):
            broken_count = index - usable_count
            print("Usable books: {}, Broken books: {}, Total books: {}".format(
                usable_count, broken_count, index))

    print("Usable books: {}, Broken books: {}, Total books: {}".format(
        usable_count, broken_count, len_initial))

# In[29]:

def add_wikipages_to_dicts():
    """
    Parses all the wikipedia links and adds valid books to `book_movie_dict`,
    and valid movies to `movie_book_dicts`.
    """
    global len_initial

    for url in wikipages:
        page = requests.get(url).text
        soup = BeautifulSoup(page, 'lxml')

        add_to_rows(soup)
        add_to_book_film_dict()

# In[52]:

def get_existing_movie_imdb_nos():
    """
    Iterates through `movie_book_dict` and fills in IMDb numbers
    from the wikipedia pages of the respective movie.
    """
    usable_count = 0

    errors = (requests.exceptions.MissingSchema or
              socket.gaierror or
              KeyError or
              requests.exceptions.ConnectionError or
              requests.exceptions.NewConnectionError or
              requests.exceptions.MaxRetryError or Exception)

    for index, key in enumerate(movie_book_dict.keys()):
        movie_book_dict[key]['usable'] = False  # default is false

        book_title = movie_book_dict[key]['book_title']
        if book_title not in book_movie_dict.keys():
            try:
                movie_book_dict[key]['imdb_no'] = get_imdb_no(key)
            except:
                movie_book_dict[key]['imdb_no'] = 'broken'

            if movie_book_dict[key]['imdb_no'] != 'broken':
                movie_book_dict[key]['usable'] = True
                print('{} ✔️'.format(book_title))
                usable_count += 1
            else:
                print('{} 𝙓'.format(book_title))

            if (index + 1) % 150 == 0:
                print('Index: {}, Usable: {} --> {}%'
                      .format(index + 1, usable_count, round(usable_count*100/(index+1), 3)))
        else:
            movie_book_dict[key]['imdb_no'] = 'broken'

# In[33]:

def add_all_imdb_lists(imdb_lists):
    """
    Iterates through `imdb_lists` and passes each indivdual
    list to add_imdb_list().
    """
    global imdb_updates

    for link in imdb_lists:
        add_imdb_list(link)
        print('\n List done. Total added: {}'.format(imdb_updates))

# In[34]:

metadata_update_count = 0

def book_metadata_refresh():
    """
    Adds book metadata to entire dict.
    """

    global metadata_update_count

    for index, key in enumerate(book_movie_dict.keys()):
        update_book_metadata(key)

        if book_movie_dict[key]['metadata_updated'] is True:
            metadata_update_count += 1
            print('{} ✔'.format(key))
        else:
            print('{} 𝙓'.format(key))

        if index % 75 == 0 and index != 0:
            print("Indexed: {}, Updated: {}, Usable: {}%"
                  .format(index, metadata_update_count, round(100*metadata_update_count/index, 3)))

# In[35]:

def get_imdb_actors(actor_string):
    actors = actor_string.rstrip('.').split(',')
    actors = [a.lower().strip() for a in actors]
    return actors

def get_imdb_writers(writer_string):
    writers = writer_string.rstrip('.').split(',')
    writers = [re.sub(r'\([^()]*\)', '', w) for w in writers]
    writers = [w.lower().strip() for w in writers]
    return writers

def get_imdb_genres(genre_string):
    genres = genre_string.rstrip('.').split(',')
    genres = [g.lower().strip() for g in genres]
    return genres

# In[37]:

def movie_metadata_refresh():
    """
    Updates move metdata for all 'usable' movies in the movie_book_dict.
    """

    updated_count = 0
    for index, key in enumerate(movie_book_dict.keys()):

        if movie_book_dict[key]['usable'] is True:
            try:
                add_imdb_metadata(key)
            except json.JSONDecodeError:
                movie_book_dict[key]['usable'] = False
                movie_book_dict[key]['imdb_no'] = 'broken'
                updated_count -= 1
                pass

            print('{} ✔'.format(movie_book_dict[key]['movie_title']))
            updated_count += 1
        else:
            print('{} 𝙓'.format(movie_book_dict[key]['movie_title']))

        if index % 150 == 0 and index != 0:
            print('Index: {}, Updated: {} --> {}%'.format(index,
                                                          updated_count, round(updated_count * 100/index), 3))

    print('Index: {}, Updated: {} --> {}%'.format(index,
                                                  updated_count, round(updated_count * 100/index), 3))

# In[163]:

def match_ids():
    """
    Creates a book_id for each book/movie, to uniquly identify a book movie pair.
    book_id = b + '_' + ISBN + '_'+ OCLC

    Creates a movie_id for each movie, to uniquly identify a book movie pair.
    movie_id = m + '_' ISBN + '_'+ OCLC + '_' + 'imdb_no'

    """
    for key in book_movie_dict.keys():
        book_movie_dict[key]['book_id'] = 'b_' + \
            book_movie_dict[key]['isbn'] + '_' + book_movie_dict[key]['oclc']
    print('Books updated.')

    for key in movie_book_dict.keys():
        movie_book_dict[key]['book_id'] = 'b_' + \
            movie_book_dict[key]['isbn'] + '_' + movie_book_dict[key]['oclc']

        movie_book_dict[key]['movie_id'] = 'm_' + movie_book_dict[key]['isbn'] + \
            '_' + movie_book_dict[key]['oclc'] + \
            '_' + movie_book_dict[key]['imdb_no']
    print('Movies updated.')

# ## Functions that webscrape (no explicit API calls)

# In[22]:

def add_to_rows(page_soup):
    """
    Method extracts row elements from the soup tags of individual
    list pages (A - F, H - J, etc.) and appends them to the `rows`
    list.

    Args:
        page_soup: (BeautifulSoup tag) soup for list page.
    """

    global rows

    tables = page_soup.find_all('table', {'class': 'wikitable'})

    for alphabet in tables:
        rows += alphabet.findAll('tr')

    print("Tables added: {}, Rows added: {}".format(len(tables), len(rows)))

# In[28]:

def get_isbn_oclc(wiki_url):
    """
    Parses the `infobox vcard` element of the wikipedia page of a book,
    and returns the 10-digit or 13-digit ISBN or 9-digit OCLC number (if found).

    Args:
        wiki_url (str): Valid (not local) wikipedia link.

    Returns:
        (dictionary) = {'isbn': isbn, 'oclc': oclc}

        isbn: Returns ISBN code is parsed correctly, 'broken' if formmated
        incorrectly or otherwise. The code is de-hyphentated for later pipeline
        efficiency.

        oclc: Returns OCLC code is parsed correctly, 'broken' if formmated
        incorrectly or otherwise.

    """
    try:
        page = requests.get(wiki_url).text
        soup = BeautifulSoup(page, 'lxml')
    except requests.exceptions.MissingSchema or Exception:
        return 'broken'

    infobox = soup.find('table', {'class': 'infobox vcard'})
    isbn, oclc = '', ''

    if infobox is None:
        isbn, oclc = 'broken', 'broken'

    else:
        isbn_found, oclc_found = False, False

        for row in infobox.findAll('tr'):
            # ISBN directly available
            if 'ISBN' in row.text and isbn_found is False:
                isbn = re.sub('[^0-9]', '', row.findAll('a')[-1].text)
                isbn_found = True

            if row.find('a', {'title': 'OCLC'}) is not None and oclc_found is False:
                oclc = row.find('td').text
                oclc = oclc.split()[0]
                oclc_found = True

        if isbn_found is False and oclc_found is False:
            isbn, oclc = 'broken', 'broken'

    return {'isbn': isbn, 'oclc': oclc}

# In[30]:

def get_imdb_no(wiki_movie):
    """
    Returns movie's respective IMDB no (if found).

    Args:
        wiki_movie: (str) Wikipedia link of movie's article.

    Returns:
        imdb_no: (str) IMDB no. if found, 'broken' otherwise.
    """
    imdb_no = ''

    errors = (requests.exceptions.MissingSchema or

              KeyError or
              requests.exceptions.ConnectionError or
              requests.exceptions.NewConnectionError or
              requests.exceptions.MaxRetryError)

    try:
        page = requests.get(wiki_movie).text
        soup = BeautifulSoup(page, 'lxml')
    except errors:
        return 'broken'

    external_links = soup.find('a', href=re.compile("imdb.com/title"))

    try:
        imdb_no = external_links['href'].split('/')[4]
    except TypeError:
        return 'broken'

    return imdb_no

# In[32]:

def add_imdb_list(imdb_list):
    """
    Adds books and movies from 1 imdb list.

    Args:
        imdb_lists: (list) Link to individual imdb list.
    """
    global imdb_updates

    new_books = {}
    new_movies = {}

    page = requests.get(imdb_list).text
    soup = BeautifulSoup(page, 'lxml')
    print('Working on: {} | {}'.format(soup.title.text, imdb_list))

    list_elements = soup.findAll('h3', {'class': 'lister-item-header'})
    list_elements = [l.find('a') for l in list_elements]
    no_elements = len(list_elements)

    for index, l in enumerate(list_elements):
        imdb_no = l['href'].split('/')[2]
        imdb_link = 'https://imdb.com' + l['href']

        movie_title = l.text

        # Get details about new books
        book_essentials = get_book_essentials_from_movie_title(movie_title)
        new_books[book_essentials['book_title']] = book_essentials

        # Get details about new movies
        movie_essentials = {'movie_title': movie_title,
                            'book_title': book_essentials['book_title'],
                            'imdb_no': imdb_no,
                            'isbn': book_essentials['isbn'],
                            'oclc': book_essentials['oclc'],
                            'usable': True}
        new_movies[imdb_link] = movie_essentials

        # Adds newly sources books and movies to initial dictionaries
        book_movie_dict.update(new_books)
        movie_book_dict.update(new_movies)

        imdb_updates += 1

        if imdb_updates % 50 == 0:
            try:
                print('Added from this list: {}, Total in this list: {}, Total added: {}'.format(
                    index, no_elements))
            except IndexError:
                pass

    return

# In[36]:

def get_box_office(imdb_no):
    """
    Scrapes a particular IMDB page for box office information.
    """

    imdb_page = 'https://www.imdb.com/title/' + imdb_no
    page = requests.get(imdb_page).text
    soup = BeautifulSoup(page, 'lxml')

    wanted = ['Budget', 'Opening Weekend USA',
              'Gross USA', 'Cumulative Worldwide Gross']
    box_office_stats = {}

    for div in soup.findAll('div', {'class': 'txt-block'}):
        try:
            subheading = div.find('h4').text.split(':')[0]
        except AttributeError:
            subheading = None
            pass

        if subheading in wanted:
            try:
                money = div.text.split(':')[1].split('\n')[0]
                money = money.replace(',', '').split()[0].split('$')[1]
            except IndexError or KeyError:
                money = 'N/A'

            subheading = subheading.lower().replace(' ', '_')
            box_office_stats[subheading] = money

    return box_office_stats

get_box_office('tt0454876')

# ## Functions with explicit API calls

# In[81]:

book_metadata_wanted = ['title', 'identifiers', 'number_of_pages', 'subject_places',
                        'subjects', 'publish_date', 'publish_places', 'author']

def update_book_metadata(book_title):
    """
    Uses the OpenLibrary and Goodreads APIs (when possible) to
    add metadata about the books to the `book_movie_dict`.

    Args:
        book_title: (str) used when merging back into `book_movie_dict`.

    Returns:
        updated: (bool) True if metadata updated, False otherwise.

    """
    metadata = {}
    all_metadata = {}

    if book_movie_dict[book_title]['valid_identifier'] is False:
        # API can't be accessed
        metadata['metadata_updated'] = False
        book_movie_dict[book_title].update(metadata)
        return

    elif book_movie_dict[book_title]['isbn'] != '':
        code = book_movie_dict[book_title]['isbn']
        curl = 'https://openlibrary.org/api/books?bibkeys=ISBN:{}&jscmd=data&format=json'.format(
            code)
        all_metadata = requests.get(curl).json()
    else:
        code = book_movie_dict[book_title]['oclc']
        curl = 'https://openlibrary.org/api/books?bibkeys=OCLC:{}&jscmd=data&format=json'.format(
            code)
        all_metadata = requests.get(curl).json()

    if len(all_metadata) > 0:
        key = list(all_metadata.keys())[0]
        nested_keys = list(all_metadata[key].keys())

        for data_point in book_metadata_wanted:
            if data_point in nested_keys:
                metadata[data_point] = all_metadata[key][data_point]

        if 'subject_places' in nested_keys:
            metadata['subject_places'] = [place['name'][:30]
                                          for place in metadata['subject_places']]
        if 'subjects' in nested_keys:
            metadata['subjects'] = [subject['name'][:30]
                                    for subject in metadata['subjects']]
        if 'publish_places' in nested_keys:
            metadata['publish_places'] = [place['name'][:30]
                                          for place in metadata['publish_places']]

        if 'identifiers' in nested_keys:
            if 'goodreads' in list(metadata['identifiers'].keys()):
                metadata['goodreads'] = metadata['identifiers']['goodreads'][0]
            metadata.pop('identifiers')

        if 'goodreads' in metadata.keys():
            metadata.update(get_goodreads_data(metadata['goodreads']))

        metadata['metadata_updated'] = True
        book_movie_dict[book_title].update(metadata)
        return

    else:
        metadata['metadata_updated'] = False
        book_movie_dict[book_title].update(metadata)
        return

# In[85]:

desired_metadata = ['average_rating',
                    'publication_date',
                    'rating_dist',
                    'ratings_count', 'format',
                    'text_reviews_count',
                    'title', 'language_code', 'author', 'authors']

def get_goodreads_data(gc_code):
    """
    Add additional reviews and ratings related meta_data from the GoodReads API.

    Args:
        gc_code: Strictly Goodreads code. Can be 10-digit or 13-digit.

    Returns:
        gr_metadata: Dict with additional metadata.
    """

    gr_metadata = {}
    try:
        book = gc.book(gc_code)
    except NameError:
        return gr_metadata
    except ExpatError:
        return gr_metadata

    for attrs in book.__dict__['_book_dict']:
        if attrs in desired_metadata:
            gr_metadata['gc_' + attrs] = book.__dict__['_book_dict'][attrs]

    return gr_metadata

# In[41]:

movie_metadata_wanted = ['Title', 'Year', 'Rated', 'Released', 'Runtime',
                         'English', 'imdbRating', 'imdbVotes']

def add_imdb_metadata(movie_url):
    """
    Adds IMDB metadata from the OMBD API.

    Args:
        movie_url: (str) essentially, the key for each movie in `movie_book_dict`.
                    Can be wikipedia link or imdb link.
    """
    metadata = {}
    all_metadata = {}
    imdb_no = movie_book_dict[movie_url]['imdb_no']

    all_metadata = requests.get(
        'http://www.omdbapi.com/?i={}&apikey=2cb213a7'.format(imdb_no)).json()

    for key in all_metadata.keys():
        if key in movie_metadata_wanted:
            metadata['imdb_' + key.lower()] = all_metadata[key]

        if 'Actors' in all_metadata.keys():
            metadata['imdb_actors'] = get_imdb_actors(all_metadata['Actors'])
        if 'Writer' in all_metadata.keys():
            metadata['imdb_writers'] = get_imdb_writers(all_metadata['Writer'])
        if 'Genre' in all_metadata.keys():
            metadata['imdb_genres'] = get_imdb_genres(all_metadata['Genre'])

    metadata.update(get_box_office(imdb_no))

    metadata['metadata_updated'] = True

    movie_book_dict[movie_url].update(metadata)

# In[236]:

def get_book_essentials_from_movie_title(movie_title):
    """
    Reverse look up of a movie's wikipedia page to identify source book.

    Returns:
        book_essentials: (dict) of book detail in the `book_movie_dict` format.
    """

    book_essentials = {}
    possible_wiki_combos = []
    isbn, oclc = '', ''
    valid_identifier = False

    # Assume that movie title is the book title
    book_title = movie_title
    wiki_link = 'https://en.wikipedia.org/wiki/' + book_title

    isbn_oclc = get_isbn_oclc(wiki_link)
    isbn = isbn_oclc['isbn']
    oclc = isbn_oclc['oclc']

    if isbn == 'broken' and oclc == 'broken':
        possible_wiki_combos.append(movie_title.replace('&', 'and'))
        possible_wiki_combos.append(movie_title + '_(novel)')
        possible_wiki_combos.append(movie_title + '_(book)')

        try:
            # Removes :
            possible_wiki_combos.append(movie_title.split(':')[1].strip())
            # Removes :
            possible_wiki_combos.append(movie_title.split(':')[
                                        1].split('-')[0].strip())
        except IndexError:
            pass

        for possible_title in possible_wiki_combos:
            wiki_link = 'https://en.wikipedia.org/wiki/' + possible_title
            isbn_oclc = get_isbn_oclc(wiki_link)
            isbn = isbn_oclc['isbn']
            oclc = isbn_oclc['oclc']

            if isbn != 'broken' or oclc != 'broken':
                book_title = possible_title
                valid_identifier = True
                break
            else:
                wiki_link = 'https://en.wikipedia.org/wiki/The ' + possible_title
                isbn_oclc = get_isbn_oclc(wiki_link)
                isbn = isbn_oclc['isbn']
                oclc = isbn_oclc['oclc']

                if isbn != 'broken' or oclc != 'broken':
                    book_title = possible_title
                    valid_identifier = True
                    break
    else:
        valid_identifier = True

    if valid_identifier is False:
        wiki_link, book_title = '', 'unknown'
    else:
        print('{} ✔'.format(book_title))

    book_essentials = {'author': '',
                       'book_title': book_title,
                       'book_wiki_url': wiki_link,
                       'count': 1,
                       'adaptations': [movie_title],
                       'isbn': isbn,
                       'oclc': oclc,
                       'valid_identifier': valid_identifier}

    return (book_essentials)

get_book_essentials_from_movie_title("Percy Jackson: Sea of Monsters")

# In[110]:

def clean_gc_authors():
    """
    Updates web-scraped authors with Goodreads info.
    """

    update = 0
    for index, key in enumerate(book_movie_dict.keys()):
        try:
            gc_authors_clean = book_movie_dict[key]['gc_authors']['author']['name']
            book_movie_dict[key]['author'] = gc_authors_clean
            print('{} ✔️'.format(key))

            del book_movie_dict[key]['gc_authors']
            update += 1

        except Exception:
            print('{} 𝙓'.format(key))
            pass
    print('Updated: {}, total: {}'.format(update, index))

# ## Start here

# ### Parse wikipedia articles to build dictionaries

# In[43]:

rows = []
book_movie_dict_all = {}
movie_book_dict = {}
sum_adaptations = 0
len_initial = 0
broken_count = 0
usable_count = 0
book_movie_dict = {}
imdb_updates = 0

add_wikipages_to_dicts()

len_initial = len(book_movie_dict_all)

# In[47]:

add_valid_books_to_dict()

# In[48]:

print(len(book_movie_dict), len(movie_book_dict))

# ### Data after Lv 1 enrichment

# In[46]:

movie_book_dict['https://en.wikipedia.org/wiki/A_Clockwork_Orange_(film)']

# In[49]:

book_movie_dict['A Clockwork Orange (1962)']

# ### Get IMDB numbers for movies provided by Wikipedia

# In[53]:

get_existing_movie_imdb_nos()

# In[54]:

movie_book_dict['https://en.wikipedia.org/wiki/A_Clockwork_Orange_(film)']

# ### Scrape IMDb lists to add new movies and books to dictionaries

# In[56]:

add_all_imdb_lists(imdb_lists)

# ### _De facto_ data size

# In[57]:

print(len(book_movie_dict), len(movie_book_dict))

# ## Enrich data using APIs

# ### Get book relatated metadata from OpenLibrary API and Goodreads APIs

# In[86]:

book_metadata_refresh()

# In[178]:

clean_gc_authors()

# ### Get book relatated metadata from IMDb API

# In[177]:

movie_metadata_refresh()

# In[179]:

lowercase_everything()

# ## Create unique pairing IDs for every movie and book

# In[180]:

match_ids()

# ### Deep copy dictionaries

# In[181]:

# DON'T RUN AGAIN
safe_book_movie_dict = copy.deepcopy(book_movie_dict)
id(safe_book_movie_dict), id(book_movie_dict)

# In[182]:

# DON'T RUN AGAINabs
safe_movie_book_dict = copy.deepcopy(movie_book_dict)
id(safe_movie_book_dict), id(movie_book_dict)

# ## Data enrichment complete!

# In[183]:

movie_book_dict['https://en.wikipedia.org/wiki/A_Clockwork_Orange_(film)']

# In[184]:

book_movie_dict['A Clockwork Orange_(novel)']

# In[185]:

movie_book_dict['https://en.wikipedia.org/wiki/Cape_Fear_(1962_film)']

# In[186]:

movie_book_dict['https://en.wikipedia.org/wiki/Cape_Fear_(1991_film)']

# ## Converting to dataframes

# In[231]:

book_movie = pd.DataFrame.from_dict(data=book_movie_dict, orient='index')
book_movie.set_index('book_id', inplace=True)
book_movie.head()

# We eliminate `broken` movies.

# In[232]:

movie_book = pd.DataFrame.from_dict(data=movie_book_dict, orient='index')
movie_book = movie_book.loc[movie_book['book_id'] != 'b_broken_broken']
movie_book = movie_book.loc[movie_book['imdb_no'] != 'broken']
movie_book.set_index('movie_id', inplace=True)
movie_book.head(5)

# ### Export to CSV

# In[234]:

# Export to csv
book_movie.to_csv('data/books.csv')
movie_book.to_csv('data/movies.csv')

# Data is finally obtained! Now we can start the real project.
