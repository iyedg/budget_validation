from budget_validation.budget_validation import app


def main():
    # TODO: configure the dash app in create_dash function
    app.run_server(debug=app.server.config["DEBUG"])


if __name__ == "__main__":
    main()
