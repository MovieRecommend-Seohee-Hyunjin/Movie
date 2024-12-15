from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

# 메인 페이지 라우트
@app.route('/', endpoint='index')
@app.route('/Main/', endpoint='index')
def showMain():
    return render_template('index.html')

# genre_all 페이지 라우트
@app.route('/genre_all/')
def showgenre_all():
    conn = sqlite3.connect('movie_recommend.db')
    cursor = conn.cursor()

    # Get distinct genres
    cursor.execute("SELECT DISTINCT Genre FROM movie")
    genres = [{'Genre': row[0]} for row in cursor.fetchall()]

    # Fetch 3 preview movies for each genre
    genre_movies = {}
    for genre in genres:
        cursor.execute("SELECT Name FROM movie WHERE Genre = ? LIMIT 3", (genre['Genre'],))
        genre_movies[genre['Genre']] = [{'Name': row[0]} for row in cursor.fetchall()]

    conn.close()

    return render_template('genre_all.html', genres=genres, genre_movies=genre_movies)

# 특정 장르의 영화 리스트 페이지 라우트
@app.route('/genre/<genre_name>')
def genre(genre_name):
    conn = sqlite3.connect('movie_recommend.db')
    cursor = conn.cursor()

    # Get movies for the specific genre
    cursor.execute("SELECT Name FROM movie WHERE Genre = ?", (genre_name,))
    movies = [{'Name': row[0]} for row in cursor.fetchall()]

    conn.close()

    return render_template('genre.html', genre_name=genre_name, movies=movies)


if __name__ == '__main__':
    app.run(debug=True)
