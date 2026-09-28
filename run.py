import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    print(f"==================================================")
    print(f"  CareerLense — See Your Career Clearly.")
    print(f"  Starting local server at http://127.0.0.1:{port}")
    print(f"  No Login Required")
    print(f"==================================================")
    app.run(host='0.0.0.0', port=port, debug=debug)
