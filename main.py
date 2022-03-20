from website import create_app
from flask_bootstrap import Bootstrap


app = create_app()
app.config["SECRET_KEY"] = "APP_SECRET_KEY"
Bootstrap(app)

if __name__ == '__main__':
    app.run(debug=True)
