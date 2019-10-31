# Server
## Description
A self-built back-end server supporting querying of bus stops, routes, etc.

## Database
### Description
This database is created with TfNSW open transport data full-table and python script.

### Link
nsw_bus2.db: [Google Drive](https://drive.google.com/open?id=17d_3RrEveQ0mKdihOkndIE76fol8g_ic)

## Setup
### Requirements
* Python 3.6
* pip 9.0 (or above)
* Flask 1.1.1
* SQLAlchemy 1.3.10
  
### Installation
To setup this back-end, first download the script and the db file together.
Follow the next steps to setup:

1. Install python3 and pip:

    #### Linux:
        
        (sudo) yum/apt-get install python3,python3-pip

    #### Windows:

    Download miniconda/anaconda, install and select `add to system path` option.

2. Install required packages with pip.

        python3 -m pip install flask, sqlalchemy


3. With cmd(windows) or bash(linux), go to the working directory:
   
        cd /path/to/dir

4. Set environment path for flask, and then start the server:

    #### Linux:

    First revise the seperator in line 12, wifi_server.py, revise '`\\`' to be '/'.

    Then in bash:

        export FLASK_APP=wifi_server.py
        python3 -m flask run [--host=0.0.0.0] [--port=8080]

    #### Windows:
    
        set FLASK_APP=wifi_server.py
        python -m flask run [--host=0.0.0.0] [--port=8080]

    The '--host' option could be '127.0.0.1' for local connection or '0.0.0.0' for connection from any network.

    The '--port' option is to specify which port the server is using locally. The port should not conflict with other ports. If not specified, default will be 5000.

5. If the server runs successfully, you can see Flask logging in the console:

         * Running on http://[host]:[port]
