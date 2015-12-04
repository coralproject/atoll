from coral import coral

# for uwsgi
app = coral.app

if __name__ == '__main__':
    coral.run(debug=True, port=5001)
