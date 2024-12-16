from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# 메인 페이지 라우트
@app.route('/', endpoint='index')
@app.route('/Main/', endpoint='index')
def showMain():
    return render_template('index.html')


# 앱 실행 시 데이터베이스와 테이블 생성
def init_db():
    conn = sqlite3.connect('movie_recommend.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_title TEXT NOT NULL,
            youtube_url TEXT NOT NULL,
            search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_name TEXT NOT NULL,
            movie_url TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    
# 검색 결과 저장 및 표시
@app.route('/search', methods=['GET'])
def search_movie():
    movie_title = request.args.get('movie_title')  # 검색창에서 입력된 영화 제목
    youtube_url = f"https://www.youtube.com/results?search_query={movie_title}"  # 유튜브 검색 URL 생성
    
    conn = sqlite3.connect('movie_recommend.db')
    cursor = conn.cursor()

    # 데이터베이스에서 영화 존재 여부 확인 (대소문자 무시)
    cursor.execute("SELECT Name FROM movie WHERE LOWER(Name) = LOWER(?)", (movie_title,))
    movie = cursor.fetchone()

    if movie:  # 영화가 데이터베이스에 존재하면 영화 설명 페이지로 이동
        conn.close()
        return redirect(url_for('movie', movie_name=movie_title))
    else:  # 영화가 데이터베이스에 없으면 YouTube 검색으로 리다이렉트
        # 검색 기록 저장
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_title TEXT NOT NULL,
                youtube_url TEXT NOT NULL,
                search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("INSERT INTO search_history (movie_title, youtube_url) VALUES (?, ?)", 
                       (movie_title, youtube_url))
        conn.commit()
        conn.close()
        return redirect(youtube_url)


# 검색 기록 표시
@app.route('/search_history')
def show_search_history():
    conn = sqlite3.connect('movie_recommend.db')
    cursor = conn.cursor()

    # 저장된 검색 기록 가져오기
    cursor.execute("SELECT movie_title, youtube_url, search_time FROM search_history")
    history = cursor.fetchall()

    conn.close()
    return render_template('search_history.html', history=history)

# 삭제
@app.route('/clear_history', methods=['POST'])
def clear_search_history():
    conn = sqlite3.connect('movie_recommend.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM search_history")  # 테이블의 모든 데이터 삭제
    conn.commit()
    conn.close()
    return redirect(url_for('show_search_history'))


# 장르 -------------------------------
@app.route('/genre_all/')
def showgenre_all():
    conn = sqlite3.connect('movie_recommend.db')
    cursor = conn.cursor()

    # Get distinct genres
    cursor.execute("SELECT DISTINCT Genre FROM movie")
    genres = [{'Genre': row[0]} for row in cursor.fetchall()]

    genre_movies = {}
    for genre in genres:
        cursor.execute("SELECT Name FROM movie WHERE Genre = ? LIMIT 3", (genre['Genre'],))
        genre_movies[genre['Genre']] = [{'Name': row[0]} for row in cursor.fetchall()]

    conn.close()
    return render_template('genre_all.html', genres=genres, genre_movies=genre_movies)

@app.route('/genre/<genre_name>')
def genre(genre_name):
    conn = sqlite3.connect('movie_recommend.db')
    cursor = conn.cursor()
    cursor.execute("SELECT Name FROM movie WHERE Genre = ?", (genre_name,))
    movies = [{'Name': row[0]} for row in cursor.fetchall()]
    conn.close()
    return render_template('genre.html', genre_name=genre_name, movies=movies)

# 평점별 영화 라우트
@app.route('/Rating/<rating_range>')
def showRating(rating_range):
    conn = sqlite3.connect('movie_recommend.db')
    cursor = conn.cursor()
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

@app.route('/Rating_all/')
def showRating_all():
    conn = sqlite3.connect('movie_recommend.db')
    cursor = conn.cursor()
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



# 즐겨찾기 추가 (중복 방지)
@app.route('/add_to_favorites/<movie_name>', methods=['POST'])
def add_to_favorites(movie_name):
    conn = sqlite3.connect('movie_recommend.db')
    cursor = conn.cursor()

    # 해당 영화의 URL 가져오기
    cursor.execute("SELECT URL FROM movie WHERE Name = ?", (movie_name,))
    result = cursor.fetchone()
    if result:
        movie_url = result[0]

        # 중복 여부 확인
        cursor.execute("SELECT * FROM favorites WHERE movie_name = ?", (movie_name,))
        existing = cursor.fetchone()
        if not existing:
            cursor.execute("INSERT INTO favorites (movie_name, movie_url) VALUES (?, ?)", 
                           (movie_name, movie_url))
            conn.commit()
    conn.close()
    return redirect(url_for('show_favorites'))

# 즐겨찾기 목록 보기
@app.route('/favorites')
def show_favorites():
    conn = sqlite3.connect('movie_recommend.db')
    cursor = conn.cursor()
    cursor.execute("SELECT movie_name, movie_url FROM favorites")
    favorites = [{'Name': row[0], 'URL': row[1]} for row in cursor.fetchall()]
    conn.close()
    return render_template('favorites.html', favorites=favorites)

# 즐겨찾기 삭제
@app.route('/delete_favorite/<movie_name>', methods=['POST'])
def delete_favorite(movie_name):
    conn = sqlite3.connect('movie_recommend.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM favorites WHERE movie_name = ?", (movie_name,))
    conn.commit()
    conn.close()
    return redirect(url_for('show_favorites'))

# 영화 세부 정보 페이지
@app.route('/movie/<movie_name>')
def movie(movie_name):
    conn = sqlite3.connect('movie_recommend.db')
    cursor = conn.cursor()
    cursor.execute("SELECT Name, Plot, URL, GPA, Year, Genre FROM movie WHERE Name = ?", (movie_name,))
    movie = cursor.fetchone()
    if movie:
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
    else:
        conn.close()
        return "Movie not found", 404

if __name__ == '__main__':
    init_db() #데이터베이스와 테이블 초기화
    app.run(debug=True)
