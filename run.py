from budget_validation.budget_validation import APP
from budget_validation.utils import get_dash_runserver_args_from_flask_config


def main():
    # TODO: configure the dash app in create_dash function
    APP.run_server(**get_dash_runserver_args_from_flask_config(APP.server.config))


if __name__ == "__main__":
    main()
