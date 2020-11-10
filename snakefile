rule run_approval_1:
    conda: "env/flask.yml"
    shell: """
        FLASK_ENV=development FLASK_APP=approval_1.py python -m flask run
    """
