import json
import logging
import os
import sqlite3
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import List

import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

logger = logging.getLogger()


def dict_factory(cursor: sqlite3.Cursor, row: tuple) -> dict:
    """Dict factory for row.
    :param cursor: sqlite3 Cursor object.
    :param row: query result.
    :return dictionary:
        {
            'col_name': value,
            ...
        }
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Role(Enum):
    WRITER = 'writer'
    ACTOR = 'actor'
    DIRECTOR = 'director'


class MovieType(Enum):
    MOVIE = 'movie'
    TV_SHOW = 'tv_show'


@dataclass
class Career:
    name: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Person:
    name: str
    role: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Genre:
    name: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Movie:
    title: str
    description: str
    rating: float
    persons: List[Person]
    genres_names: List[str]
    id: uuid.UUID = field(default_factory=uuid.uuid4)


class SQLiteLoader:
    SQL = '''
    WITH x as (
        /* Using group_concat to get ids and names of all actors into one list after join with the actors table
        Notice that order of ids and names are same
        Remeber that movies and actors tables have m2m relationship */
        SELECT m.id, group_concat(a.name) as actors_names, group_concat(a.id) as actors_ids
        FROM movies m
        LEFT JOIN movie_actors ma ON m.id = ma.movie_id
        LEFT JOIN actors a ON ma.actor_id = a.id
        GROUP BY m.id
    )
    -- Get list of all movies with writers and actors
    SELECT m.id, genre, director, title, plot, imdb_rating, x.actors_ids, x.actors_names,
        /* This CASE is solution for the problem in the table design:
        if there is only one writer, then it saved as simple string in the writer column. 
        Otherwise data storage in writers column as json object.
        For fix this issue we use hack:
        transform single value of writer into list of a single json object and put all in the writers column. */
            CASE
                WHEN m.writers = '' THEN '[{"id": "' || m.writer || '"}]'
                ELSE m.writers
            END AS writers
    FROM movies m
    LEFT JOIN x ON m.id = x.id
    '''

    def __init__(self, conn:sqlite3.Connection):
        self.conn = conn
        self.conn.row_factory = dict_factory

    def load_writers(self) -> dict:
        """Get list of all writers, cause there is no way to get all writers in a single request.
        :return: dict of all writers of the form:
            {
                'writer_id': 'writer_name'
            }
        """
        writers = {}

        for writer in self.conn.execute('SELECT DISTINCT id, name FROM writers'):
            writers[writer['id']] = writer['name']
        
        return writers

    def _transform_row(self, row: dict, writers: dict) -> Movie:
        """The main logic for converting data from SQLite to an internal representation,
        which will futher go to PostgreSQL.
        Problems solved:
        1) genre on the sqldatabase is specified as a string of one or more genres,
        separated by commas -> convert to a list of Genre objects.
        2) writers from a query in the sqldatabase comes in the form of a list of id's dictionaries ->
        we look up correct names by ids using previously obtained all writers' names and ids then 
        create Person object for each writer.
        3) using query field (actors_names) we create new Person object for each actor name.
        4) for the imdb_rating, description fields -> change the 'N/A' fields to Null.
        5) for directors, writers, actors -> do not create Person object if name is N/A.
        """
        # Collect all related persons(actors, directors, writers) to the movie.
        persons = []

        writers_set = set()

        for writer in json.loads(row['writers']):
            writer_id = writer['id']
            if writers[writer_id] != 'N/A' and writer_id not in writers_set:
                persons.append(
                    Person(name=writers[writer_id], role=Role.WRITER.value))
                writers_set.add(writer_id)

        if row['actors_names'] is not None:
            persons.extend([
                Person(name=name, role=Role.ACTOR.value) for name in row['actors_names'].split(',')
                if name != 'N/A'
            ])

        if row['director'] != 'N/A':
            persons.extend([
                Person(name=x.strip(), role=Role.DIRECTOR.value) for x in row['director'].split(',')])

        return Movie(
            title=row['title'],
            description=row['plot'] if row['plot'] != 'N/A' else '',
            rating=float(row['imdb_rating']) if row['imdb_rating'] != 'N/A' else None,
            persons=persons,
            genres_names=[name for name in row['genre'].replace(' ', '').split(',')],
        )
 
    def load_movies(self) -> List[Movie]:
        """The main method for loading all movies from SQLite database.
        :return: list of dictionaries of trasformed data of movies.
        """
        movies = []

        writers = self.load_writers()

        for row in self.conn.execute(self.SQL):
            transform_row = self._transform_row(row, writers)
            movies.append(transform_row)

        return movies


class PostgresSaver:

    def __init__(self, pg_conn: _connection):
        self.pg_conn = pg_conn

    def save_all_data(self, data: List[dict]):
        """Main method for saving prepared data from SQLite database to Postgres database.
        :param data: list of dictionaries of trasformed data of movies from SQLite database.
        """
        cursor = pg_conn.cursor()

        # first insert known roles
        # create dict of careers for later to determine of correct id of career
        careers = {}

        for role in Role:
            career = Career(role.value)
            careers[career.name] = career

        args = ','.join(cursor.mogrify("(%s, %s, NOW(), NOW())", (
            str(career.id), career.name)).decode() for career in careers.values())

        cursor.execute(f"""
        INSERT INTO content.career (id, name, created_at, updated_at)
        VALUES {args}
        """)

        # second insert known movies' types
        # create dict of movies types for later to determine of correct id of movie type
        movies_types_dict = dict()

        for movie_type in MovieType:

            movies_types_dict[movie_type.value] = str(uuid.uuid4())
            cursor.execute("""
            INSERT INTO content.filmwork_type (id, name, created_at, updated_at)
            VALUES (%s, %s, NOW(), NOW())
            """, (movies_types_dict[movie_type.value], movie_type.value))

        # Store created genres
        genres_dict = dict()

        for movie in data:

            cursor.execute("""
                INSERT INTO content.filmwork (
                    id, title, description, rating, type_id, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT (id) DO NOTHING""", (
                str(movie.id), 
                movie.title, 
                movie.description, 
                movie.rating,
                movies_types_dict['movie'],
                ))

            for genre_name in movie.genres_names:

                if genre_name not in genres_dict:
                    genre = Genre(genre_name)
                    cursor.execute("""
                        INSERT INTO content.genre (id, name, created_at, updated_at)
                        VALUES (%s, %s, NOW(), NOW())
                        ON CONFLICT (id) DO NOTHING""", (str(genre.id), genre.name))
                    genres_dict[genre.name] = str(genre.id)

                # Insert row in association table for m2m relationship of movie and genre entities
                cursor.execute("""
                    INSERT INTO content.genres_filmworks (
                        id, filmwork_id, genre_id, created_at)
                    VALUES (%s, %s, %s, now())
                    ON CONFLICT DO NOTHING""", (
                    str(uuid.uuid4()), 
                    str(movie.id), 
                    genres_dict[genre_name],
                    ))

            for person in movie.persons:

                cursor.execute("""
                    INSERT INTO content.person (id, full_name, created_at, updated_at)
                    VALUES (%s, %s, NOW(), NOW())
                    ON CONFLICT (id) DO NOTHING""", (
                    str(person.id), 
                    person.name,
                    ))

                # Insert row in association table for m2m relationship of movie and person entities
                career_id = str(careers[person.role].id)
                cursor.execute("""
                INSERT INTO content.careers_persons(
                    id, career_id, person_id, created_at)
                VALUES (%s, %s, %s, NOW())
                ON CONFLICT DO NOTHING""", (
                    str(uuid.uuid4()),
                    career_id,
                    str(person.id),
                    )
                )

                # Insert row in association table for m2m relationship of movie and person entities
                cursor.execute("""
                    INSERT INTO content.persons_filmworks (
                        id, filmwork_id, person_id, role_id, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    ON CONFLICT DO NOTHING""", (
                    str(uuid.uuid4()),
                    str(movie.id),
                    str(person.id),
                    career_id,
                    ))


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""
    postgres_saver = PostgresSaver(pg_conn)
    sqlite_loader = SQLiteLoader(connection)

    data = sqlite_loader.load_movies()
    postgres_saver.save_all_data(data)


if __name__ == '__main__':

    basedir = os.path.abspath(os.path.dirname(__file__))

    load_dotenv(os.path.join(basedir, '.env_load_data'))

    dsn = {
        'dbname': os.environ.get('SD_POSTGRES_DBNAME'), 
        'user': os.environ.get('SD_POSTGRES_USER'),
        'password': os.environ.get('SD_POSTGRES_PASSWORD'),
        'host': os.environ.get('SD_POSTGRES_HOST', 'localhost'), 
        'port': os.environ.get('SD_POSTGRES_PORT', 5432)
        }

    with sqlite3.connect('db.sqlite') as sqlite_conn, psycopg2.connect(**dsn, cursor_factory=DictCursor) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
