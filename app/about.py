from flask import render_template

def init_about_routes(app):
    @app.route('/', methods=['GET', 'POST'])
    @app.route('/about', methods=['GET', 'POST'])
    def about():
        return render_template('about.html')
