echo "setting local environment variables for authentication..."
export ACCESS_TOKEN_URI='https://sdk.efs.ai/auth/realms/efs-sdk/protocol/openid-connect/token'
echo "setting local environment variables for accessmanager..."
export UPLOAD_ENDPOINT='https://sdk.efs.ai/accessmanager/api/v2.0/accessmanager/upload/main'
export DELETE_ENDPOINT='https://sdk.efs.ai/accessmanager/api/v2.0/accessmanager/delete'
export READ_ENDPOINT='https://sdk.efs.ai/accessmanager/api/v2.0/accessmanager/read'