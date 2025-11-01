from eventapp import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

    # turn to false to see 500 error