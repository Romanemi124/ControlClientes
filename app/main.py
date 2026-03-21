from app.database.models import create_tables

def main():
    create_tables()
    print("Base de datos creada correctamente")

if __name__ == "__main__":
    main()