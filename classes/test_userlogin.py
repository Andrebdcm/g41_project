from classes.userlogin import Userlogin

# Clear previous data
Userlogin.obj.clear()
Userlogin.lst.clear()

# Test creating users
admin = Userlogin(None, 'admin', 'admin', Userlogin.set_password('senha123'))
user = Userlogin(None, 'joao', 'user_only', Userlogin.set_password('senha456'))

print("=== Testes de Utilizadores ===")
print(f'Admin criado: {admin}')
print(f'Utilizador criado: {user}')

print("\n=== Testes de Métodos de Classe ===")
print(f'ID do admin: {Userlogin.get_user_id("admin")}')
print(f'ID do joao: {Userlogin.get_user_id("joao")}')

print("\n=== Testes de Password ===")
result_admin = Userlogin.chk_password("admin", "senha123")
print(f'Password admin (correta): {result_admin}')
print(f'Username armazenado: {Userlogin.username}')
print(f'User ID armazenado: {Userlogin.user_id}')

result_wrong = Userlogin.chk_password("joao", "errada")
print(f'Password joao (errada): {result_wrong}')

result_nouser = Userlogin.chk_password("inexistente", "senha")
print(f'Utilizador inexistente: {result_nouser}')

print("\n=== Testes de Find ===")
find_admin = Userlogin.find('admin', 'user')
print(f'Encontrado por username: {find_admin}')

find_by_group = Userlogin.find('admin', 'usergroup')
print(f'Encontrado por usergroup: {find_by_group}')

print("\n=== Testes de Type Checking ===")
print(f'Admin é admin: {admin.is_admin()}')
print(f'Admin é user_only: {admin.is_user_only()}')
print(f'Utilizador é admin: {user.is_admin()}')
print(f'Utilizador é user_only: {user.is_user_only()}')


