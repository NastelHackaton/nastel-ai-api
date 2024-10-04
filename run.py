from dotenv import load_dotenv
from app import create_app

load_dotenv()

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
