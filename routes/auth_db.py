import boto3
from flask import Blueprint, jsonify, request

auth_db_bp = Blueprint('auth_db', __name__)

# Initialize the DynamoDB client
dynamodb = boto3.client('dynamodb', region_name='ap-southeast-1',
                        aws_access_key_id='YOUR_ACCESS_KEY_ID',
                        aws_secret_access_key='YOUR_SECRET_ACCESS_KEY')

# Define the DynamoDB table name for the User model
user_table_name = 'User'


@auth_db_bp.route('/users', methods=['GET'])
def get_users():
    try:
        response = dynamodb.scan(TableName=user_table_name)
        items = response.get('Items', [])
        users = [dict((k, v['S']) for k, v in item.items()) for item in items]
        return jsonify(users)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_db_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    try:
        response = dynamodb.get_item(
            TableName=user_table_name,
            Key={'user_id': {'N': str(user_id)}
                 }
        )
        item = response.get('Item')
        if item:
            user = dict((k, v['S']) for k, v in item.items())
            return jsonify(user)
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_db_bp.route('/users/<string:username>', methods=['GET'])
def get_user_by_username(username):
    try:
        response = dynamodb.get_item(
            TableName=user_table_name,
            Key={'username': {'S': username}
                 }
        )
        item = response.get('Item')
        if item:
            user = dict((k, v['S']) for k, v in item.items())
            return jsonify(user)
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_db_bp.route('/users', methods=['POST'])
def create_user():
    try:
        user_data = request.json
        dynamodb.put_item(
            TableName=user_table_name,
            Item={k: {'S': str(v)} for k, v in user_data.items()}
        )
        return jsonify({'message': 'User created successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add more authentication-related routes
