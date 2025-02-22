Create Tables using Migrations:
Once the database exists, you can use Flask-Migrate to create the necessary tables based on your models.

If you haven't already initialized migrations, run the following commands:

Initialize Migrations:

bash
Copy
flask db init```

Generate the Migration Script:

bash
Copy
flask db migrate -m "Initial migration"
Apply the Migration:

bash
Copy
flask db upgrade
This will create the tables in the QuickRecieptDb database based on the models you've defined.

test