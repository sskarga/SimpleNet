# SimpleNet - simple network management programm. (Python, Flask)

## Install

    pip install -r requirements.txt
    
Migration

    flask db init
    flask db migrate -m "start"
    flask db upgrade
    
Init db. Create default user admin.

    flask init admin