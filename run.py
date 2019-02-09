from budget_validation.budget_validation import app
from budget_validation.utils import get_dash_runserver_args_from_flask_config
from pprint import pprint


def main():
    # TODO: configure the dash app in create_dash function
    app.run_server(**get_dash_runserver_args_from_flask_config(app.server.config))


if __name__ == "__main__":
    main()
