import os
import app as planner
import unittest
import tempfile

# source: http://flask.pocoo.org/docs/0.12/testing/

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, planner.app.config['DATABASE'] = tempfile.mkstemp()
        planner.app.testing = True
        self.app = planner.app.test_client()
        with planner.app.app_context():
            planner.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(planner.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'No assignment entries here so far' in rv.data

    # modified login() code from the following source
    # http://flask.pocoo.org/docs/0.12/testing/
    def add_entry(self, title, course, category, duedate, description):
        return self.app.post('/add',
            data=dict(title=title, course=course, category=category, duedate=duedate, description=description),
            follow_redirects=True)

    def test_add_entry(self):

        rv = self.add_entry('title1', 'CS253', 'None', '1111-11-11T11:11', 'D1')
        assert b"title1" in rv.data
        assert b"New assignment was successfully saved." in rv.data

    def delete_entry(self, delete):
        return self.app.post('/delete', data=dict(id=delete), follow_redirects=True)

    def test_delete_entry(self):

        rv = self.add_entry('title1', 'CS253.1', 'None', '1111-11-11T11:11', 'D1')
        assert b"title1" in rv.data

        rv = self.add_entry('title2', 'CS253.2', 'None', '1111-11-11T11:11', 'D2')
        assert b"title2" in rv.data

        rv = self.add_entry('title3', 'CS253.3', 'None', '1111-11-11T11:11', 'D3')
        assert b"title3" in rv.data

        # delete second post
        rv = self.delete_entry(2)
        assert b"title2" not in rv.data


        # then, delete the top post (with id=3)
        rv = self.delete_entry(3)
        assert b"title3" not in rv.data
        assert b"title1" in rv.data

        # then, delete the remaining post (with id=1)
        rv = self.delete_entry(1)
        assert b"title1" not in rv.data

    def edit_entry(self, title, course, category, duedate, description, id):
        return self.app.post('/edit_assignment',
            data=dict(title=title, course=course, category=category, duedate=duedate, description=description, id=id),
            follow_redirects=True)

    def test_edit_entry(self):
        rv = self.add_entry('title1', 'CS253.1', 'None', '1111-11-11T11:11', 'D1')
        assert b"title1" in rv.data

        # test case for when title is edited as empty
        rv = self.edit_entry('title1-edit', 'CS253.1-edit', 'None-edit', '2222-22-22T22:22', 'D1-edit', 1)
        assert b"title1-edit" in rv.data
        assert b"CS253.1-edit" in rv.data
        assert b"None-edit" in rv.data
        assert b"2222-22-22T22:22" in rv.data
        assert b"D1-edit" in rv.data

if __name__ == '__main__':
    unittest.main()