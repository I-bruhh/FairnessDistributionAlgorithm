import boto3
from flask import jsonify


# Initialize the DynamoDB client
dynamodb = boto3.client('dynamodb')

# Define the DynamoDB table name for Concerts
concerts_table_name = 'Concerts'


def get_all_concerts():
    try:
        # Access the DynamoDB table to list all concerts
        response = dynamodb.scan(
            TableName=concerts_table_name
        )
        print(response)
        items = response.get('Items', [])
        concerts = []
        print(items)
        for item in items:
            formatted_item = {
                "concert_id": item["concert_id"]["N"],
                "name": item["name"]["S"],
                "dates": [date["S"] for date in item["dates"]["L"]],
                "venues": [venue["S"] for venue in item["venues"]["L"]],
                "categories": [int(category["N"]) for category in item["categories"]["L"]],
                "start_ticket_sale": item["start_ticket_sale"]["S"],
                "end_ticket_sale": item["end_ticket_sale"]["S"],
                "limit_per_person": int(item["limit_per_person"]["N"]),
                "total_tickets_for_sale": int(item["total_tickets_for_sale"]["N"]),
            }
            concerts.append(formatted_item)
        return jsonify(concerts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
            concert = []
            formatted_item = {
                "concert_id": item["concert_id"]["N"],
                "name": item["name"]["S"],
                "dates": [date["S"] for date in item["dates"]["L"]],
                "venues": [venue["S"] for venue in item["venues"]["L"]],
                "categories": [int(category["N"]) for category in item["categories"]["L"]],
                "start_ticket_sale": item["start_ticket_sale"]["S"],
                "end_ticket_sale": item["end_ticket_sale"]["S"],
                "limit_per_person": int(item["limit_per_person"]["N"]),
                "total_tickets_for_sale": int(item["total_tickets_for_sale"]["N"]),
            }
            concert.append(formatted_item)
            return jsonify(concert)
        else:
            return jsonify({'message': 'Concert not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
