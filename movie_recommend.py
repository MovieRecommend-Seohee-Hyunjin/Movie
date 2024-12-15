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
    conn.commit()
    conn.close()


# 검색 결과 저장 및 표시
@app.route('/search', methods=['GET'])
def search_movie():
    movie_title = request.args.get('movie_title')  # 검색창에서 입력된 값
    youtube_url = f"https://www.youtube.com/results?search_query={movie_title}"  # 유튜브 검색 URL 생성
    
    # 데이터베이스에 검색 기록 저장
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
    cursor.execute("INSERT INTO search_history (movie_title, youtube_url) VALUES (?, ?)", 
                   (movie_title, youtube_url))
    conn.commit()
    conn.close()

    # 검색 결과 페이지로 전달
    return render_template('search_results.html', movie_title=movie_title, youtube_url=youtube_url)

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

# 특정 영화의 세부 정보 보기
@app.route('/movie/<movie_name>')
def movie(movie_name):
    conn = sqlite3.connect('movie_recommend.db')
    cursor = conn.cursor()
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
