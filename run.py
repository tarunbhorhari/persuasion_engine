from settings import app
from settings.app_settings import Settings

if __name__ == "__main__":
    Settings.initialize_app()
    app.run()
