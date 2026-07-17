"""Seed the database with initial data for demo/testing."""
from app.database import SessionLocal, engine
from app import models
from app.utils.auth import hash_password
from datetime import date, timedelta

def seed():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(models.User).first():
        print("DB already seeded. Skipping.")
        db.close()
        return

    # Admin user
    admin = models.User(name="Admin", email="admin@cinebook.com",
                        hashed_password=hash_password("admin123"), is_admin=True)
    # Regular user
    user = models.User(name="John Doe", email="user@cinebook.com",
                       hashed_password=hash_password("user123"))
    db.add_all([admin, user])
    db.commit()

    # Screens
    s1 = models.Screen(name="Screen 1", total_rows=6, seats_per_row=8)
    s2 = models.Screen(name="Screen 2", total_rows=8, seats_per_row=10)
    db.add_all([s1, s2])
    db.commit()

    # Movies
    movies_data = [
        {"title": "Inception", "description": "A thief who steals corporate secrets through dream-sharing technology.", "genre": "Sci-Fi / Thriller", "language": "English", "duration_mins": 148, "rating": 8.8, "poster_url": "https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg"},
        {"title": "The Dark Knight", "description": "Batman faces the Joker, a criminal mastermind who wants to plunge Gotham into anarchy.", "genre": "Action / Drama", "language": "English", "duration_mins": 152, "rating": 9.0, "poster_url": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg"},
        {"title": "Interstellar", "description": "A team of explorers travel through a wormhole in space to ensure humanity's survival.", "genre": "Sci-Fi / Adventure", "language": "English", "duration_mins": 169, "rating": 8.6, "poster_url": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg"},
        {"title": "Parasite", "description": "Greed and class discrimination threaten the newly formed symbiotic relationship between two families.", "genre": "Drama / Thriller", "language": "Korean", "duration_mins": 132, "rating": 8.5, "poster_url": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg"},
        {"title": "Avengers: Endgame", "description": "The Avengers assemble to undo Thanos's actions and restore order to the universe.", "genre": "Action / Adventure", "language": "English", "duration_mins": 181, "rating": 8.4, "poster_url": "https://image.tmdb.org/t/p/w500/or06FN3Dka5tukK1e9sl16pB3iy.jpg"},
        {"title": "RRR", "description": "A fictional story about two legendary revolutionaries and their journey before they began their fight against the British.", "genre": "Action / Drama", "language": "Telugu", "duration_mins": 182, "rating": 7.8, "poster_url": "https://image.tmdb.org/t/p/w500/nEufeZlyAOLqO2brrs0yeF1lgXO.jpg"},
    ]
    movies = []
    for m in movies_data:
        movie = models.Movie(**m)
        db.add(movie)
        movies.append(movie)
    db.commit()

    # Showtimes for next 3 days
    times = ["10:00 AM", "1:30 PM", "4:00 PM", "7:30 PM", "10:30 PM"]
    today = date.today()
    for i, movie in enumerate(movies):
        for day_offset in range(3):
            show_date = (today + timedelta(days=day_offset)).strftime("%Y-%m-%d")
            for t_idx, show_time in enumerate(times[:3]):
                screen = s1 if (i + t_idx) % 2 == 0 else s2
                st = models.Showtime(
                    movie_id=movie.id, screen_id=screen.id,
                    show_date=show_date, show_time=show_time,
                    price=250.0 + (50.0 * (t_idx % 2))
                )
                db.add(st)
    db.commit()
    db.close()
    print("✅ Database seeded successfully!")
    print("   Admin: admin@cinebook.com / admin123")
    print("   User:  user@cinebook.com  / user123")

if __name__ == "__main__":
    seed()
