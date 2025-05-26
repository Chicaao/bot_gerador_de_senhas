import sqlite3
import hashlib
import contextlib

DATABASE_NAME = 'password_bot.db'

@contextlib.contextmanager

def get_db_cursor():
    """
    Gerenciador de contexto que produz um cursor de banco de dados e garante que a conexão seja fechada.
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        yield cursor #Fornece o cursor a ser usado no bloco ‘with’.
        conn.commit() #Confirmar as alterações se não houver exceções
    except Exception as e:
        if conn:
            conn.rollback() #Reversão em caso de erro
        raise #Aumentar novamente a exceção
    finally: 
        if conn:
            conn.close() #Verifique se a conexão está fechada

def create_tables():
    """Cria as tabelas de usuários e senhas se elas não existirem."""
    with get_db_cursor() as cursor:
        #Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')

        # Tabela de senhas geradas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS generated_passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                password TEXT NOT NULL, -- CUIDADO: Armazenando senhas em texto puro, em um app real seria criptografado
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        '''
        )

def hash_password(password):
    """Gera um hash SHA256 da senha."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    """
    Cadastra um novo usuário no banco de dados.
    Retorna True em sucesso, False em falha (usuário já existe).
    """
    try:
        with get_db_cursor() as cursor:
            password_hash = hash_password(password)
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
            return True
    except sqlite3.IntegrityError:
        print(f"Erro: Usuário '{username}' já existe.")
        return False
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante o registro: {e}")
        return False

def authenticate_user(username, password):
    """
    Autentica um usuário.
    Retorna o ID do usuário se a autenticação for bem-sucedida, caso contrário, None.
    """
    with get_db_cursor() as cursor:
        password_hash = hash_password(password)
        cursor.execute("SELECT id FROM users WHERE username = ? AND password_hash = ?", (username, password_hash))
        user = cursor.fecthone()
    if user:
        return user[0]
    return None

def save_generated_password(user_id, description, password):
    """Salva uma senha gerada para um usuário específico."""
    with get_db_cursor() as cursor:
        cursor.execute("INSERT INTO generated_passwords (user_id, description, password) VALUES (?, ?, ?)",
                        (user_id, description, password))

def get_user_passwords(user_id):
    """Retorna todas as senhas geradas para um usuário específico."""
    with get_db_cursor() as cursor:
        cursor.execute("SELECT description, password FROM generated_passwords WHERE user_id = ?", (user_id,))
        passwords = cursor.fetchall()
    return passwords

#Inicializa o banco de dados e tabelas ao importar
create_tables()



