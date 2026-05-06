DB_USER = "shopuser"
DB_PASSWORD = "12345"
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "onlineshopping"

SQLALCHEMY_DATABASE_URI = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
SECRET_KEY = "dev-secret-key"
