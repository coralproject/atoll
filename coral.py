from coral import coral

app = coral.create_app()

# for debugging
# check /var/log/coral.log
# app.config['DEBUG'] = True
# app.config['PROPAGATE_EXCEPTIONS'] = True

if __name__ == '__main__':
    app.run(debug=True, port=5001)
