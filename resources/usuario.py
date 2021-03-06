from flask_restful import Resource, reqparse
from models.usuario import UserModel
from flask_jwt_extended import create_access_token, jwt_required, get_raw_jwt
from werkzeug.security import safe_str_cmp
from blacklist import BLACKLIST

atributos = reqparse.RequestParser()   
atributos.add_argument('login', type=str, required=True, help="The field 'login' might be informed.")  
atributos.add_argument('senha', type=str, required=True, help="The field 'senha' might be informed.")  

class User(Resource):
    # /usuarios/{user_id}

    def get(self, user_id):
        user = UserModel.find_user(user_id)
        
        if user:
            return user.json()
        return {'message': 'User not found'}, 404 # not found 

    @jwt_required
    def delete(self, user_id):
        user = UserModel.find_user(user_id)

        if user:
            try:
                user.delete_user()
            except:
                return {'message': 'An internal error occurred trying to delete user.'}, 500 # internal server error   
            return {'message': 'User deleted'} 
        return {'message': 'User not found'}, 404 # not found

class UserRegister(Resource):
    # /cadastro

    def post(self):
        dados = atributos.parse_args()
        
        if UserModel.find_by_login(dados['login']):
            return {"message": "User login '{}' already exists.".format(dados['login'])}, 400
        
        user_obj = UserModel(**dados )
        
        try:
            user_obj.save_user()
            return {'message': 'User created successfully!'}, 201 # created
        except:
            return {'message': 'An internal error occurred trying to save user.'}, 500 # internal server error  
        return user_obj.json(), 201 # created       

class UserLogin(Resource):

    @classmethod
    def post(cls):
        dados = atributos.parse_args()

        user = UserModel.find_by_login(dados['login'])

        if user and safe_str_cmp(user.senha, dados['senha']):
            token_acesso = create_access_token(identity=user.user_id)
            return {'access_token': token_acesso}, 200 
        return {'message': 'User or password incorrect'}, 401 # unauthorized

class UserLogout(Resource):   
    
    @jwt_required
    def post(self):     
        jwt_id = get_raw_jwt()['jti'] #JWT Token Identifier
        BLACKLIST.add(jwt_id)
        return {'message': 'Logged out successfully!'}, 200 
