from flask_jwt_extended import create_access_token

token = create_access_token(
    identity=user["email"],         
    additional_claims={
        "role": user["role"]          
    }
)
