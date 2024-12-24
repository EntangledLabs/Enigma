

from parable.logger import write_log_header
from parable import create_app

if __name__ == '__main__':
    # Initialize logger
    write_log_header()

    app = create_app()
    app.run(debug=True)