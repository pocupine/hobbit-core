import pytest

from webargs.core import ValidationError
from hobbit_core.flask_hobbit.pagination import PageParams, pagination

from . import BaseTest
from .models import User
from .exts import db


class TestPagination(BaseTest):

    def test_page_params(self, web_request, parser):
        # test default
        @parser.use_kwargs(PageParams, web_request, locations=('query', ))
        def viewfunc(page, page_size, order_by):
            return {'page': page, 'page_size': page_size, 'order_by': order_by}

        assert viewfunc() == {'order_by': ['-id'], 'page': 1, 'page_size': 10}

        # test page_size_range
        web_request.query = {'page_size': 101}
        msg = "webargs.core.ValidationError: {'page_size': " + \
            "['Must be between 10 and 100.']}"
        with pytest.raises(ValidationError, message=msg):
            viewfunc()

        # test order_by
        web_request.query = {'order_by': 'id,-11'}
        msg = "webargs.core.ValidationError: {'order_by': " + \
            "{1: ['String does not match expected pattern.']}}"
        with pytest.raises(ValidationError, message=msg):
            viewfunc()

        web_request.query = {'order_by': 'id,-aaa'}
        assert viewfunc() == {
            'order_by': ['id', '-aaa'], 'page': 1, 'page_size': 10}

        web_request.query = {'order_by': ''}
        assert viewfunc() == {
            'order_by': [''], 'page': 1, 'page_size': 10}

    def test_pagination(self, client):
        user1 = User(username='test1', email='1@b.com', password='1')
        user2 = User(username='test2', email='1@a.com', password='1')
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        # test ?order_by= worked
        resp = pagination(User, 1, 10, order_by=[''])
        assert resp['total'] == 2
        assert resp['page_size'] == 10
        assert resp['page'] == 1
        assert [i.id for i in resp['items']] == [1, 2]

        resp = pagination(User, 1, 10, order_by=['role'])
        assert [i.id for i in resp['items']] == [1, 2]

        resp = pagination(User, 1, 10, order_by=['role', '-id'])
        assert [i.id for i in resp['items']] == [2, 1]

        resp = pagination(User, 1, 10, order_by=['role', 'username'])
        assert [i.id for i in resp['items']] == [1, 2]
