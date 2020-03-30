from flask import Flask, request
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow, fields

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))  # Less than 255 chars
    content = db.Column(db.Text)
    topics = db.relationship("Topic", backref='addtopost', lazy=True)


class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))


class TopicSchema(ma.Schema):
    class Meta:
        model = Topic
        fields = ('id', 'description')


class PostSchema(ma.Schema):
    class Meta:
        model = Post
        fields = ('id', 'title', 'content', "topics")
    topics = fields.fields.Nested(TopicSchema, many=True)


post_schema = PostSchema()
posts_schema = PostSchema(many=True)


class PostsResource(Resource):
    def get(self):  # list all posts
        with app.test_request_context():
            return posts_schema.dump(Post.query.all())

    def post(self):  # insert a new post
        data = request.json  # Receive data in JSON format
        post = Post(title=data['title'], content=data['content'])
        db.session.add(post)
        db.session.commit()
        return  # post_schema.dump(post)  # Return serialized data


class PostResource(Resource):
    def get(self, pk):  # list a single post - pk = id
        return # post_schema.dump(Post.query.get_or_404(pk))

    def patch(self, pk):  # modify a post
        data = request.json
        post = Post.query.get_or_404(pk)

        if 'title' in data or 'content' in data:
            post.title = data['title']
            post.content = data['content']

        db.session.commit()
        return # post_schema.dump(post)

    def delete(self, pk): # delete a post
        post = Post.query.get_or_404(pk)
        db.session.delete(post)
        db.session.commit()
        return '', 204


api.add_resource(PostResource, '/posts/<int:pk>')
api.add_resource(PostsResource, '/posts')

if __name__ == '__main__':
    db.create_all()
    # Insert Manually a Record
    # post1 = Post(title="Terminator IV", content="Movie that talks about the future John Connor")
    # topic1 = Topic(description="Sci-fi", addtopost=post1)
    # topic2 = Topic(description="War", addtopost=post1)
    # db.session.add_all([post1, topic1, topic2])
    # db.session.commit()
    app.run(port=8001, debug=True)
