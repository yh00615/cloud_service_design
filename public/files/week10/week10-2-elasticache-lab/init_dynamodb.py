"""DynamoDB 테이블 초기화 스크립트"""
import boto3
import os

region = os.getenv('AWS_DEFAULT_REGION', 'ap-northeast-2')
table_name = os.getenv('DYNAMODB_TABLE', 'week10-2-elasticache-lab-APIData')

dynamodb = boto3.resource('dynamodb', region_name=region)
table = dynamodb.Table(table_name)

users = [
    {'id': '1', 'name': '김철수', 'email': 'kim@example.com', 'age': 28, 'city': 'Seoul'},
    {'id': '2', 'name': '이영희', 'email': 'lee@example.com', 'age': 32, 'city': 'Busan'},
    {'id': '3', 'name': '박민수', 'email': 'park@example.com', 'age': 25, 'city': 'Incheon'},
    {'id': '4', 'name': '정수진', 'email': 'jung@example.com', 'age': 30, 'city': 'Daegu'},
    {'id': '5', 'name': '최지훈', 'email': 'choi@example.com', 'age': 27, 'city': 'Gwangju'},
    {'id': '6', 'name': '강미영', 'email': 'kang@example.com', 'age': 29, 'city': 'Daejeon'},
    {'id': '7', 'name': '윤서준', 'email': 'yoon@example.com', 'age': 31, 'city': 'Ulsan'},
    {'id': '8', 'name': '임하은', 'email': 'lim@example.com', 'age': 26, 'city': 'Suwon'},
    {'id': '9', 'name': '한동현', 'email': 'han@example.com', 'age': 33, 'city': 'Changwon'},
    {'id': '10', 'name': '오지원', 'email': 'oh@example.com', 'age': 24, 'city': 'Goyang'},
]

print('DynamoDB 테이블 초기화 중...')
with table.batch_writer() as batch:
    for user in users:
        batch.put_item(Item=user)
print(f'{len(users)}개의 사용자 데이터가 추가되었습니다.')
