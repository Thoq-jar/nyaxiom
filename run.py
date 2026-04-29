from quart import Quart


def create_app() -> Quart:
    app: Quart = Quart(__name__, template_folder="templates", static_url_path="/static")

    try:
        import os

        os.makedirs(app.instance_path)
    except OSError:
        print("warn: could not create instance folder!")

    from src.routes.api.routes import api_bp
    from src.routes.main.routes import main_bp

    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(main_bp, url_prefix="/")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
