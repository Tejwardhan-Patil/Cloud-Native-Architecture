from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Configuration for the database connection
DATABASE_URI = "postgresql://username:password@host:port/database"

# Define the engine and metadata object
engine = create_engine(DATABASE_URI)
metadata = MetaData(bind=engine)

# Session for executing queries
Session = sessionmaker(bind=engine)
session = Session()

# Function to create a new table
def create_table():
    try:
        new_table = Table(
            'new_table', metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(255), nullable=False),
            Column('email', String(255), unique=True),
        )
        new_table.create(engine)
        print("New table created successfully.")
    except SQLAlchemyError as e:
        print(f"Error creating table: {e}")

# Function to alter an existing table (add new column)
def add_column_to_table():
    try:
        table = Table('existing_table', metadata, autoload=True)
        new_column = Column('new_column', String(255))
        new_column.create(table, populate_default=True)
        print("Column added successfully.")
    except SQLAlchemyError as e:
        print(f"Error adding column: {e}")

# Function to drop a column from a table
def drop_column_from_table():
    try:
        table = Table('existing_table', metadata, autoload=True)
        if 'column_to_drop' in table.c:
            drop_col = table.c.column_to_drop.drop()
            print("Column dropped successfully.")
        else:
            print("Column does not exist.")
    except SQLAlchemyError as e:
        print(f"Error dropping column: {e}")

# Function to rename a column in a table
def rename_column():
    try:
        table = Table('existing_table', metadata, autoload=True)
        with engine.connect() as connection:
            connection.execute('ALTER TABLE existing_table RENAME COLUMN old_column TO new_column')
        print("Column renamed successfully.")
    except SQLAlchemyError as e:
        print(f"Error renaming column: {e}")

# Function to add a foreign key constraint to a table
def add_foreign_key():
    try:
        table = Table('child_table', metadata, autoload=True)
        fk_constraint = ForeignKey('parent_table.id')
        table.append_constraint(fk_constraint)
        metadata.create_all(engine)
        print("Foreign key added successfully.")
    except SQLAlchemyError as e:
        print(f"Error adding foreign key: {e}")

# Function to drop a table
def drop_table():
    try:
        table_to_drop = Table('table_to_drop', metadata, autoload=True)
        table_to_drop.drop(engine)
        print("Table dropped successfully.")
    except SQLAlchemyError as e:
        print(f"Error dropping table: {e}")

# Function to run custom SQL commands
def run_custom_sql():
    try:
        with engine.connect() as connection:
            connection.execute("ALTER TABLE existing_table ADD COLUMN another_column VARCHAR(100)")
            print("Custom SQL executed successfully.")
    except SQLAlchemyError as e:
        print(f"Error running custom SQL: {e}")

# Function to create multiple tables in a single transaction
def create_multiple_tables():
    try:
        with engine.begin() as connection:
            table1 = Table(
                'table_one', metadata,
                Column('id', Integer, primary_key=True),
                Column('data', String(255))
            )
            table2 = Table(
                'table_two', metadata,
                Column('id', Integer, primary_key=True),
                Column('description', String(255))
            )
            table1.create(connection)
            table2.create(connection)
            print("Multiple tables created successfully.")
    except SQLAlchemyError as e:
        print(f"Error creating tables: {e}")

# Function to migrate data between tables
def migrate_data():
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT * FROM old_table")
            for row in result:
                connection.execute(
                    "INSERT INTO new_table (name, email) VALUES (:name, :email)",
                    name=row['name'], email=row['email']
                )
            print("Data migration completed successfully.")
    except SQLAlchemyError as e:
        print(f"Error migrating data: {e}")

# Function to alter the data type of a column
def alter_column_data_type():
    try:
        with engine.connect() as connection:
            connection.execute("ALTER TABLE existing_table ALTER COLUMN column_name TYPE VARCHAR(500)")
            print("Column data type altered successfully.")
    except SQLAlchemyError as e:
        print(f"Error altering column data type: {e}")

# Function to execute all migrations
def execute_migrations():
    print("Starting migration process...")
    create_table()
    add_column_to_table()
    drop_column_from_table()
    rename_column()
    add_foreign_key()
    drop_table()
    run_custom_sql()
    create_multiple_tables()
    migrate_data()
    alter_column_data_type()
    print("Migration process completed.")

if __name__ == "__main__":
    execute_migrations()