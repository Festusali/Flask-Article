import os, datetime
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql+psycopg2://{os.environ.get('POSTGRE_USER')}:{os.environ.get('POSTGRE_PASSWORD')}@{os.environ.get('POSTGRE_HOST')}/{os.environ.get('POSTGRE_DB_NAME')}"


app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
ma =Marshmallow(app)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.Text())
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, title, body):
        self.title = title
        self.body = body

    def __string__(self):
        return self.title


class ArticleSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "body", "date")
    

article_schema = ArticleSchema()
articles_schema = ArticleSchema(many=True)


@app.route("/", methods=['GET'])
def get_articles():
    all_articles = Article.query.all()
    results = articles_schema.dump(all_articles)
    return jsonify(results)


@app.route('/article/<id>/', methods=['GET'])
def get_article(id):
    article = Article.query.get(id)
    return article_schema.jsonify(article)


@app.route("/add/", methods=['POST'])
def add_article():
    title = request.get_json()['title']
    body = request.get_json()['body']

    articles = Article(title, body)
    db.session.add(articles)
    db.session.commit()
    return article_schema.jsonify(articles)


@app.route('/update/<id>/', methods=['PUT'])
def update_article(id):
    article = Article.query.get(id)
    title = request.get_json().get('title')
    body = request.get_json().get('body')
    article.title = title
    article.body = body
    db.session.commit()
    return article_schema.jsonify(article)


@app.route('/delete/<id>/', methods=['DELETE'])
def delete_article(id):
    article = Article.query.get(id)
    db.session.delete(article)
    db.session.commit()
    return jsonify({"delete": "Successful"})


if __name__ == "__name__":
    app.run(debug=True)