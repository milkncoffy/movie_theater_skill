from lxml import html
import requests
from finder_app.finder_logging import *
from finder_app.finder_errors import *


class Movie:
    def __init__(self):
        self.title = None
        self.most_wanted_title = None
        self.id = None

    def update(self, entities):
        for field, value in entities.items():
            if field in self.__dict__.keys():
                self.__setattr__(field, value)

    def is_mandatory_filled(self):
        return bool(self.title)


class MovieSeance:
    def __init__(self):
        self.theatre = None
        self.date = None
        self.time = None
        self.place = None
        self.price = None
        self.language = 'RUS'
        self.format = '2D'

    def update(self, entities):
        for field, value in entities.items():
            if field in self.__dict__.keys():
                self.__setattr__(field, value)

    def is_mandatory_filled(self):
        # TODO change to comment
        # return bool(self.date) and bool(self.time) and bool(self.price)
        return bool(self.date)


class Place:
    def __init__(self):
        self.address = None
        self.subway = []


class Query:
    def __init__(self):
        self.movie = Movie()
        self.requested_seance = MovieSeance()
        self.is_mandatory_filled = False

    def update(self, entity_dict):
        self.movie.update(entity_dict)
        self.requested_seance.update(entity_dict)
        self.is_mandatory_filled = self.movie.is_mandatory_filled() and self.requested_seance.is_mandatory_filled()


def retrieve_webpage(url):
    page = requests.get(url)
    if page.status_code != 200:
        raise FailedRequestError(url)
    else:
        return page


class MovieFinder:
    def __init__(self, query):
        self.search_movie_url = 'https://www.kinopoisk.ru/index.php?kp_query='
        self.list_movie_url = 'https://www.afisha.ru/msk/schedule_cinema/{}/'
        self.movie_schedule_url = 'https://www.afisha.ru/msk/schedule_cinema_product/{}/{}/'
        self.query = query
        self.logger = get_custom_logger('../../ProjectLogs/movie_theatre_skill/tmp.log')

    afisha_date_mapper = {'01': '', '02': '', '03': 'marta', '04': 'aprelya', '05': 'maya', '06': '',
                          '07': '', '08': '', '09': '', '10': '', '11': '', '12': ''}

    def search_movie_info(self):
        url = self.search_movie_url + self.query.movie.title
        try:
            page = retrieve_webpage(url)
        except FailedRequestError as e:
            self.logger.error(e)
            return None

        tree = html.fromstring(page.content)

        try:
            search_results = tree.xpath('//div[@class="search_results"]')[0]
            most_wanted_result = search_results.xpath('//div[@class="element most_wanted"]')[0]
            most_wanted_result_info = most_wanted_result.xpath('div[@class="info"]')[0].xpath('p[@class="name"]')[0]
            movie_info = most_wanted_result_info.find('a')
            self.query.movie.most_wanted_title = movie_info.text.lower()

        except Exception as e:
            self.logger.error(e)
            raise UnexpectedPageStructureError(url) from e

        return self.query

    def find_movie_id(self, query):

        query_date = '-'.join([self.query.requested_seance.date.strftime('%d'), self.afisha_date_mapper[query.requested_seance.date.strftime('%m')]])
        url = self.list_movie_url.format(query_date)
        try:
            page = requests.get(url)
        except FailedRequestError as e:
            self.logger.error(e)
            return self.query
        tree = html.fromstring(page.content.decode('utf-8'))

        try:
            search_results = tree.xpath('//li[@class="boardItem___3bfHo wide___mGuM8 "]')
            for result in search_results:
                movie_info = result.find('section').find('h3').find('a')
                title = movie_info.text
                if title.lower() in (query.movie.title, query.movie.most_wanted_title):
                    query.movie.id = movie_info.get('href').strip('/').split('/')[-1]
                    break
        except Exception as e:
            self.logger.error(e)
            raise UnexpectedPageStructureError(url) from e

        return query

    def get_movie_schedule(self, query):
        url = self.movie_schedule_url.format(query.movie.id, query.requested_seance.date.strftime('%d-%m-%Y'))
        try:
            page = requests.get(url)
        except FailedRequestError as e:
            self.logger.error(e)
            return None

        tree = html.fromstring(page.content.decode('utf-8'))
        seance_list = []

        try:
            search_results = tree.xpath('//li[@class="unit__schedule-row"]')
            for theatre_schedule in search_results:

                theatre, place = '', ''
                schedule_meta = theatre_schedule.find('div')
                for info in schedule_meta.findall('div'):
                    if info.get('class') == 'unit__movie-name':
                        theatre = info.find('a').text
                    if info.get('class') == 'unit__movie-location':
                        place = info.text

                timetable = theatre_schedule.find('ul')
                for seance in timetable.findall('li'):
                    ms = MovieSeance()
                    ms.theatre = theatre
                    ms.place = place
                    movie_format = seance.xpath('small[@class="tooltip__body"]')
                    if len(movie_format) > 0 and type(movie_format[0].text) == str:
                        formats = [x for x in movie_format[0].text.split(' ') if 'D' in x]
                        ms.format = ms.format if len(formats) == 0 else formats[0]
                    price = seance.xpath('span[@class="timetable__item-price"]')
                    if len(price) > 0:
                        ms.price = price[0].text
                    lang = seance.xpath('span[@class="timetable__item-sub"]')
                    if len(lang) and lang[0] is not None:
                        try:
                            ms.language = lang[0].find('span').text
                        except AttributeError:
                            pass
                    ms.time = seance.find('time').text
                    seance_list.append(ms)
        except Exception as e:
            self.logger.error(e)
            raise UnexpectedPageStructureError(url) from e

        return seance_list


def get_seance_list(query):
    mf = MovieFinder(query)
    try:
        kinopoisk_query_update = mf.search_movie_info()
        if kinopoisk_query_update is not None:
            query = kinopoisk_query_update
    except UnexpectedPageStructureError:
        return None

    try:
        query = mf.find_movie_id(query)
    except UnexpectedPageStructureError:
        print('Sorry, I cannot find anything :(')
        return None
    try:
        seance_list = mf.get_movie_schedule(query)
        return seance_list
    except UnexpectedPageStructureError:
        return None