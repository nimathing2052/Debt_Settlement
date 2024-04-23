from app import create_app
from app.models import db  # Correctly import db from models package

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=9888)
