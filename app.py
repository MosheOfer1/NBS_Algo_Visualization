from dotenv import load_dotenv
import os
from app import app

load_dotenv()

if __name__ == '__main__':
    app.run(debug=os.environ.get('DEBUG', 'True') == 'True')
