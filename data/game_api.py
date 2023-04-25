import flask

from . import db_session
from .users import User

blueprint = flask.Blueprint(
    'news_api',
    __name__,
    template_folder='templates'
)



@blueprint.route('/api/game')
def get_news():
    db_sess = db_session.create_session()
    user = db_sess.query(User).all()
    return flask.jsonify(
        {
            'users':
                [item.to_dict(only=('id', 'name', 'about', 'skin', 'bestscore', 'money'))
                 for item in user]
        }
    )


@blueprint.route('/api/game/<int:game_id>', methods=['GET'])
def get_one_user(game_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(game_id)
    if not user:
        return flask.jsonify({'error': 'Not found'})
    return flask.jsonify(
        {
            'user': user.to_dict(only=(
                'id', 'name', 'about', 'skin', 'bestscore', 'money'))
        }
    )

@blueprint.route('/api/money/<int:game_id>/<int:num_money>', methods=['GET'])
def change_money(game_id, num_money):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(game_id)
    if not user:
        return flask.jsonify({'error': 'Not found'})
    user.money = num_money
    db_sess.commit()
    return flask.jsonify({'success': 'OK'})


@blueprint.route('/api/score/<int:game_id>/<int:num_score>', methods=['GET'])
def change_score(game_id, num_score):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(game_id)
    if not user:
        return flask.jsonify({'error': 'Not found'})
    user.bestscore = num_score
    db_sess.commit()
    return flask.jsonify({'success': 'OK'})