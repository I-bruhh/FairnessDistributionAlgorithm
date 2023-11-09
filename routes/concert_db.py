import boto3
from flask import Blueprint, jsonify

concert_db_bp = Blueprint('concert_db', __name__)

# Initialize the DynamoDB client
dynamodb = boto3.client('dynamodb', region_name='ap-southeast-1',
                        aws_access_key_id='YOUR_ACCESS_KEY_ID',
                        aws_secret_access_key='YOUR_SECRET_ACCESS_KEY')

# Define the DynamoDB table name for Concerts
concerts_table_name = 'Concerts'


@concert_db_bp.route('/concerts', methods=['GET'])
def get_all_concerts():
    try:
        # Access the DynamoDB table to list all concerts
        response = dynamodb.scan(
            TableName=concerts_table_name
        )
        items = response.get('Items', [])
        concerts = [dict((k, v['S']) for k, v in item.items()) for item in items]
        return jsonify(concerts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@concert_db_bp.route('/concert/<int:concert_id>', methods=['GET'])
def get_concert_by_id(concert_id):
    try:
        # Access the DynamoDB table to get a specific concert by concert_id
        response = dynamodb.get_item(
            TableName=concerts_table_name,
            Key={
                'concert_id': {
                    'N': str(concert_id)
                }
            }
        )
        item = response.get('Item')
        if item:
            concert = dict((k, v['S']) for k, v in item.items())
            return jsonify(concert)
        else:
            return jsonify({'message': 'Concert not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Other functions for creating, updating, and deleting concerts can be added here
