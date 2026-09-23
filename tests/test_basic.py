def test_project_imports():

    from app.main import app

    assert (
        app.title
        ==
        "Real-Time Messaging System"
    )