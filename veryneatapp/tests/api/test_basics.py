from fastapi import FastAPI


"""
Whenever you need the client to pass information in the request
and you don't know how to, you can search (Google) how to do it in requests.
http://docs.python-requests.org/

E.g.:
To pass a path or query parameter, add it to the URL itself.
To pass a JSON body, pass a Python object (e.g. a dict) to the parameter json.
If you need to send Form Data instead of JSON, use the data parameter instead.
To pass headers, use a dict in the headers parameter.
For cookies, a dict in the cookies parameter. 
"""


class TestBasicsEndpoints:
    def test_get_tutorial(self, mock_client: FastAPI):
        response = mock_client.get(
            "/api/v1/basics/tutorial",
            headers={"X-Token": "fake-super-secret-token"},
        )
        assert response.status_code == 200
        assert response.json() == {"message": ["this is another route"]}

    def test_get_tutorial_invalid_header(self, mock_client: FastAPI):
        response = mock_client.get(
            "/api/v1/basics/tutorial", headers={"X-Token": "oops"}
        )
        assert response.status_code == 400
        assert response.json() == {"detail": "X-Token header invalid"}
