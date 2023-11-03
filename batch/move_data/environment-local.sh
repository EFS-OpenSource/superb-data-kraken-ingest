echo "setting local environment variables for authentication..."
export ACCESS_TOKEN_URI='https://$(DOMAIN)/auth/realms/$(REALM)/protocol/openid-connect/token'
echo "setting local environment variables for accessmanager..."
export UPLOAD_ENDPOINT='https://$(DOMAIN)/accessmanager/api/v2.0/accessmanager/upload/main'
export DELETE_ENDPOINT='https://$(DOMAIN)/accessmanager/api/v2.0/accessmanager/delete'
export READ_ENDPOINT='https://$(DOMAIN)/accessmanager/api/v2.0/accessmanager/read'