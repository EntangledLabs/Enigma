from parable import create_app

if __name__ == '__main__':


    # Run server
    app = create_app()
    app.run(debug=True)