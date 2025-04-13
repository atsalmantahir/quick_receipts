from app import create_app
from app.seed import seed_data

app = create_app()

if __name__ == "__main__":
    # Ensure app context is active before calling seed_data
    with app.app_context():
        seed_data()  # Call seed_data() inside the app context
        app.run(debug=True)
