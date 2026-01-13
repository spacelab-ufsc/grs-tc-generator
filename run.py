from app import create_app

app = create_app()

if __name__ == '__main__':
    # Run the Flask development server
    # host='0.0.0.0' allows access from outside the container (if using Docker)
    # debug=True enables auto-reload on code changes
    app.run(host='0.0.0.0', port=5000, debug=True)