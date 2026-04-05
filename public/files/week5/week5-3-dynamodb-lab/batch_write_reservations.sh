#!/bin/bash
# QuickTable 예약 데이터 일괄 입력 스크립트
# 사용법: bash batch_write_reservations.sh

REGION="ap-northeast-2"
TABLE_NAME="QuickTableReservations"

echo "QuickTable 예약 데이터를 DynamoDB 테이블에 입력합니다..."
echo "테이블: $TABLE_NAME"
echo "리전: $REGION"
echo ""

aws dynamodb batch-write-item \
  --region $REGION \
  --request-items file://sample_reservations.json

if [ $? -eq 0 ]; then
  echo ""
  echo "✅ 10개 예약 데이터가 성공적으로 입력되었습니다."
else
  echo ""
  echo "❌ 데이터 입력에 실패했습니다. AWS CLI 설정과 테이블 이름을 확인하세요."
fi
