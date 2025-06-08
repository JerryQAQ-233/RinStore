from app import create_app

SECRET_KEY = '1145141919810'

app = create_app(SECRET_KEY=SECRET_KEY)

if __name__ == '__main__':
    app.run(debug=True)


