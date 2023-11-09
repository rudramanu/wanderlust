from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:rudramanu@localhost/wanderlust'
db = SQLAlchemy(app)


try:
    db.create_all()  
    print("Database Connected Successfully")
except Exception as e:
    print("Something went wrong while connecting with the database")
    print(str(e))

if __name__ == "__main__":
    app.run()
