from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5401, debug=False)
    #csrf.init_app(app)
