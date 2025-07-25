import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://www.film2movie.asia"

def get_tags():
    url = f"{BASE_URL}/tags/"
    res = requests.get(url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    tags = soup.find_all("a", class_="tag-cloud-link")
    tag_links = [tag['href'] for tag in tags]
    return tag_links

def get_movies_from_tag(tag_url):
    movies = []
    url = tag_url
    while url:
        print(f"Processing tag page: {url}")
        res = requests.get(url)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        movie_elements = soup.select("h2.entry-title a")
        for movie in movie_elements:
            title = movie.text.strip()
            link = movie['href']
            movies.append({"title": title, "link": link})

        next_page = soup.find("a", class_="next page-numbers")
        if next_page and 'href' in next_page.attrs:
            url = next_page['href']
            time.sleep(1)
        else:
            url = None
    return movies

def extract_movie_details(post_url):
    res = requests.get(post_url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    # اگر لینک ادامه مطلب وجود داشت برو صفحه بعدی تا لینک‌های دانلود را کامل بگیریم
    more_link = soup.find("a", class_="more-link")
    if more_link and more_link.text.strip().startswith("برای مشاهده ادامه مطلب"):
        next_url = more_link['href']
        res2 = requests.get(next_url)
        res2.raise_for_status()
        soup2 = BeautifulSoup(res2.text, "html.parser")

        # لینک‌های دانلود را از صفحه ادامه مطلب می‌گیریم
        download_links = []
        for a in soup2.find_all("a", href=True):
            if "لینک مستقیم" in a.text:
                download_links.append(a['href'])
    else:
        download_links = []
        for a in soup.find_all("a", href=True):
            if "لینک مستقیم" in a.text:
                download_links.append(a['href'])

    # کاور فیلم
    poster = soup.find("img", id="myimg")
    poster_src = poster['src'] if poster else ""

    # ژانر
    genre_span = soup.find('span', style=lambda v: v and '#fa5705' in v)
    genre = genre_span.get_text(strip=True) if genre_span else ""

    # لینک imdb
    imdb_link = ""
    imdb_a = soup.find("a", href=lambda x: x and "imdb.com/title" in x)
    if imdb_a:
        imdb_link = imdb_a['href']

    # امتیاز imdb
    imdb_rate = ""
    rate_span = soup.find('span', style=lambda v: v and '#ffffff' in v)
    if rate_span:
        imdb_rate = rate_span.text.strip()

    # اطلاعات فنی
    info = {}
    p_blocks = soup.find_all("p")
    for p in p_blocks:
        text = p.get_text(" ", strip=True)
        if 'مدت زمان' in text or 'زبان' in text:
            parts = text.split('،')
            for part in parts:
                if ':' in part:
                    key, val = part.split(':', 1)
                    info[key.strip()] = val.strip()

    # ستارگان
    stars = ""
    star_span = None
    for span in soup.find_all("span", style=lambda v: v and '#fa5705' in v):
        if '،' in span.text and len(span.text.split('،')) > 1:
            stars = span.text.strip()
            star_span = span
            break

    # کارگردان
    director = ""
    if star_span:
        next_director = star_span.find_next('span', style=lambda v: v and '#fa5705' in v)
        if next_director:
            director = next_director.text.strip()

    # خلاصه داستان
    summary_div = soup.find("div", style=lambda s: s and 'width: 508px' in s and 'margin-top: 1px' in s)
    summary = summary_div.text.strip() if summary_div else ""

    return {
        "poster": poster_src,
        "genre": genre,
        "imdb_link": imdb_link,
        "imdb_score": imdb_rate,
        "movie_info": info,
        "stars": stars,
        "director": director,
        "summary": summary,
        "download_links": download_links,
    }

def main():
    tags = get_tags()
    print(f"Found {len(tags)} tags.")

    all_movies_details = {}
    for tag_link in tags:
        print(f"\nTag: {tag_link}")
        movies = get_movies_from_tag(tag_link)
        print(f" - Found {len(movies)} movies.")

        movies_details = []
        for movie in movies:
            print(f"   Extracting: {movie['title']}")
            details = extract_movie_details(movie['link'])
            movies_details.append({**movie, **details})
            time.sleep(1)

        all_movies_details[tag_link] = movies_details

    # نمونه چاپ اطلاعات (می‌توانید به فایل ذخیره کنید)
    for tag, movies in all_movies_details.items():
        print(f"\nTag: {tag} - Total movies: {len(movies)}")
        for movie in movies:
            print(f"Title: {movie['title']}")
            print(f"Link: {movie['link']}")
            print(f"Poster: {movie['poster']}")
            print(f"Genre: {movie['genre']}")
            print(f"IMDb Link: {movie['imdb_link']}")
            print(f"IMDb Score: {movie['imdb_score']}")
            print(f"Info: {movie['movie_info']}")
            print(f"Stars: {movie['stars']}")
            print(f"Director: {movie['director']}")
            print(f"Summary: {movie['summary']}")
            print(f"Download Links: {movie['download_links']}")
            print("-" * 80)

if __name__ == "__main__":
    main()
