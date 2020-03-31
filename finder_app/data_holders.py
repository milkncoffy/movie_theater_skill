class SessionStorage:
    def __init__(self):
        self._sessions = dict()

    def add_session(self, session_id, session_obj):
        self._sessions[session_id] = session_obj

    def get_session(self, session_id):
        return self._sessions[session_id]


# Here will be a storage for cash data from recent requests (like movie id from afisha)
class AfishaMovieStorage:
    def __init__(self):
        self._movies = dict()

    def add_movie(self, movie):
        self._movies[movie.movie_id] = movie

    def delete_movie(self, movie_id):
        self._movies.pop(movie_id)