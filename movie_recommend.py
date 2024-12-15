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



if __name__ == '__main__':
    app.run(debug=True)
