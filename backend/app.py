from flask_app import create_app

app = create_app()


@app.after_request
def set_default_content_type(response):
    response.headers["Content-Type"] = "application/json"
    return response


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)
