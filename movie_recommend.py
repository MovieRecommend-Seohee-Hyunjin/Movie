from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

# 메인 페이지 라우트
@app.route('/', endpoint='index')
@app.route('/Main/', endpoint='index')
def showMain():
    return render_template('index.html')

# 장르 -------------------------------
# genre_all  페이지 라우트
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
#---------------------------------------------
# 평점별 영화 라우트
@app.route('/Rating/<rating_range>')
def showRating(rating_range):
    conn = sqlite3.connect('movie_recommend.db')
    cursor = conn.cursor()

    # 평점대에 따른 SQL 쿼리
    if rating_range == '9점대':
        cursor.execute("SELECT Name, GPA FROM movie WHERE GPA >= 9 AND GPA < 10")
    elif rating_range == '8점대':
        cursor.execute("SELECT Name, GPA FROM movie WHERE GPA >= 8 AND GPA < 9")
    elif rating_range == '7점대':
        cursor.execute("SELECT Name, GPA FROM movie WHERE GPA >= 7 AND GPA < 8")
    else:
        return "Invalid rating range", 404

    movies = [{'Name': row[0], 'GPA': row[1]} for row in cursor.fetchall()]

    conn.close()
    return render_template('Rating.html', rating_range=rating_range, movies=movies)

# 모든 평점 보기
@app.route('/Rating_all/')
def showRating_all():
    conn = sqlite3.connect('movie_recommend.db')
    cursor = conn.cursor()

    # 평점대별 영화 가져오기
    ratings = ['9점대', '8점대', '7점대', '6점대']
    rating_movies = {}
    for rating in ratings:
        if rating == '9점대':
            cursor.execute("SELECT Name, GPA FROM movie WHERE GPA >= 9 AND GPA < 10 LIMIT 3")
        elif rating == '8점대':
            cursor.execute("SELECT Name, GPA FROM movie WHERE GPA >= 8 AND GPA < 9 LIMIT 3")
        elif rating == '7점대':
            cursor.execute("SELECT Name, GPA FROM movie WHERE GPA >= 7 AND GPA < 8 LIMIT 3")
        elif rating == '6점대':
            cursor.execute("SELECT Name, GPA FROM movie WHERE GPA >= 6 AND GPA < 7 LIMIT 3")
        rating_movies[rating] = [{'Name': row[0], 'GPA': row[1]} for row in cursor.fetchall()]

    conn.close()
    return render_template('Rating_all.html', ratings=ratings, rating_movies=rating_movies)


# -------------------------------------------
# 연대별 영화 전체 보기
@app.route('/Date_all/')
def showDate_all():
    conn = sqlite3.connect('movie_recommend.db')
    cursor = conn.cursor()

    # 연대별 영화 가져오기
    decades = ['2000s', '2010s', '2020s']
    decade_movies = {}
    for decade in decades:
        if decade == '2000s':
            cursor.execute("SELECT Name, Year FROM movie WHERE Year BETWEEN 2000 AND 2009 LIMIT 3")
        elif decade == '2010s':
            cursor.execute("SELECT Name, Year FROM movie WHERE Year BETWEEN 2010 AND 2019 LIMIT 3")
        elif decade == '2020s':
            cursor.execute("SELECT Name, Year FROM movie WHERE Year BETWEEN 2020 AND 2029 LIMIT 3")
        decade_movies[decade] = [{'Name': row[0], 'Year': row[1]} for row in cursor.fetchall()]

    conn.close()
    return render_template('Date_all.html', decades=decades, decade_movies=decade_movies)

# 특정 연대의 영화 보기
@app.route('/Date/<decade>')
def showDate(decade):
    conn = sqlite3.connect('movie_recommend.db')
    cursor = conn.cursor()

    # 특정 연대의 영화 가져오기
    if decade == '2000s':
        cursor.execute("SELECT Name, Year FROM movie WHERE Year BETWEEN 2000 AND 2009")
    elif decade == '2010s':
        cursor.execute("SELECT Name, Year FROM movie WHERE Year BETWEEN 2010 AND 2019")
    elif decade == '2020s':
        cursor.execute("SELECT Name, Year FROM movie WHERE Year BETWEEN 2020 AND 2029")
    else:
        return "Invalid decade", 404

    movies = [{'Name': row[0], 'Year': row[1]} for row in cursor.fetchall()]

    conn.close()
    return render_template('Date.html', decade=decade, movies=movies)

# 특정 영화의 세부 정보 보기
@app.route('/movie/<movie_name>')
def movie(movie_name):
    conn = sqlite3.connect('movie_recommend.db')
    cursor = conn.cursor()

    # 특정 영화의 정보 가져오기
    cursor.execute("SELECT Name, Plot, URL, GPA, Year, Genre FROM movie WHERE Name = ?", (movie_name,))
    movie = cursor.fetchone()

    movie_details = {
        'Name': movie[0],
        'Plot': movie[1],
        'URL': movie[2],
        'GPA': movie[3],
        'Year': movie[4],
        'Genre': movie[5]
    }

    conn.close()
    return render_template('movie.html', movie=movie_details)


if __name__ == '__main__':
    app.run(debug=True)
