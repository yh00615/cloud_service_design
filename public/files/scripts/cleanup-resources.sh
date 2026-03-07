#!/bin/bash

################################################################################
# AWS 실습 리소스 자동 정리 스크립트
# 
# 이 스크립트는 Week 태그를 기반으로 실습에서 생성한 AWS 리소스를 자동으로 삭제합니다.
# AWS CloudShell 또는 로컬 환경에서 실행할 수 있습니다.
#
# 사용법:
#   ./cleanup-resources.sh <Week-Tag-Value>
#   예: ./cleanup-resources.sh 5-3
#
# 주의사항:
#   - 반드시 올바른 Week 태그 값을 입력하세요
#   - 잘못된 태그 값으로 실행하면 다른 실습의 리소스가 삭제될 수 있습니다
#   - 삭제 전 Tag Editor로 리소스 목록을 먼저 확인하는 것을 권장합니다
################################################################################

set -e  # 오류 발생 시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Week 태그 값 확인
if [ -z "$1" ]; then
    echo -e "${RED}오류: Week 태그 값을 입력하세요${NC}"
    echo "사용법: $0 <Week-Tag-Value>"
    echo "예: $0 5-3"
    exit 1
fi

WEEK_TAG="$1"
REGION="ap-northeast-2"

# AWS 자격 증명 확인
echo -e "${BLUE}=== AWS 자격 증명 확인 ===${NC}"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
if [ -z "$ACCOUNT_ID" ]; then
    echo -e "${RED}오류: AWS 자격 증명을 찾을 수 없습니다${NC}"
    echo "AWS CloudShell을 사용하거나 'aws configure'를 실행하세요"
    exit 1
fi

echo -e "${GREEN}계정 ID: $ACCOUNT_ID${NC}"
echo -e "${GREEN}리전: $REGION${NC}"
echo ""

# 삭제 확인
echo -e "${YELLOW}경고: Week=$WEEK_TAG 태그를 가진 모든 리소스를 삭제합니다${NC}"
echo -e "${YELLOW}계속하시겠습니까? (yes/no)${NC}"
read -r CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${BLUE}작업이 취소되었습니다${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}=== Week=$WEEK_TAG 태그를 가진 리소스 삭제 시작 ===${NC}"
echo ""

################################################################################
# 1. Lambda 함수 삭제
################################################################################
echo -e "${BLUE}1. Lambda 함수 삭제 중...${NC}"
LAMBDA_COUNT=0

aws lambda list-functions --region $REGION --query "Functions[].FunctionName" --output text 2>/dev/null | \
while read -r function; do
    if [ ! -z "$function" ]; then
        tags=$(aws lambda list-tags --resource arn:aws:lambda:$REGION:$ACCOUNT_ID:function:$function \
            --region $REGION --query "Tags.Week" --output text 2>/dev/null)
        
        if [ "$tags" == "$WEEK_TAG" ]; then
            echo -e "  ${GREEN}✓${NC} Lambda 함수 삭제: $function"
            aws lambda delete-function --function-name $function --region $REGION 2>/dev/null || \
                echo -e "  ${RED}✗${NC} 삭제 실패: $function"
            LAMBDA_COUNT=$((LAMBDA_COUNT + 1))
        fi
    fi
done

if [ $LAMBDA_COUNT -eq 0 ]; then
    echo -e "  ${YELLOW}→${NC} Lambda 함수를 찾을 수 없습니다"
fi
echo ""

################################################################################
# 2. DynamoDB 테이블 삭제
################################################################################
echo -e "${BLUE}2. DynamoDB 테이블 삭제 중...${NC}"
DYNAMODB_COUNT=0

aws dynamodb list-tables --region $REGION --query "TableNames" --output text 2>/dev/null | \
while read -r table; do
    if [ ! -z "$table" ]; then
        tags=$(aws dynamodb list-tags-of-resource \
            --resource-arn arn:aws:dynamodb:$REGION:$ACCOUNT_ID:table/$table \
            --region $REGION --query "Tags[?Key=='Week' && Value=='$WEEK_TAG']" --output text 2>/dev/null)
        
        if [ ! -z "$tags" ]; then
            echo -e "  ${GREEN}✓${NC} DynamoDB 테이블 삭제: $table"
            aws dynamodb delete-table --table-name $table --region $REGION 2>/dev/null || \
                echo -e "  ${RED}✗${NC} 삭제 실패: $table"
            DYNAMODB_COUNT=$((DYNAMODB_COUNT + 1))
        fi
    fi
done

if [ $DYNAMODB_COUNT -eq 0 ]; then
    echo -e "  ${YELLOW}→${NC} DynamoDB 테이블을 찾을 수 없습니다"
fi
echo ""

################################################################################
# 3. S3 버킷 삭제
################################################################################
echo -e "${BLUE}3. S3 버킷 삭제 중...${NC}"
S3_COUNT=0

aws s3api list-buckets --query "Buckets[].Name" --output text 2>/dev/null | \
while read -r bucket; do
    if [ ! -z "$bucket" ]; then
        tags=$(aws s3api get-bucket-tagging --bucket $bucket 2>/dev/null | \
            jq -r '.TagSet[] | select(.Key=="Week" and .Value=="'$WEEK_TAG'") | .Value' 2>/dev/null)
        
        if [ "$tags" == "$WEEK_TAG" ]; then
            echo -e "  ${GREEN}✓${NC} S3 버킷 비우는 중: $bucket"
            aws s3 rm s3://$bucket --recursive 2>/dev/null || true
            
            echo -e "  ${GREEN}✓${NC} S3 버킷 삭제: $bucket"
            aws s3api delete-bucket --bucket $bucket --region $REGION 2>/dev/null || \
                echo -e "  ${RED}✗${NC} 삭제 실패: $bucket (버킷이 비어있지 않거나 버전 관리가 활성화되어 있을 수 있습니다)"
            S3_COUNT=$((S3_COUNT + 1))
        fi
    fi
done

if [ $S3_COUNT -eq 0 ]; then
    echo -e "  ${YELLOW}→${NC} S3 버킷을 찾을 수 없습니다"
fi
echo ""

################################################################################
# 4. EC2 인스턴스 종료
################################################################################
echo -e "${BLUE}4. EC2 인스턴스 종료 중...${NC}"

instance_ids=$(aws ec2 describe-instances \
    --region $REGION \
    --filters "Name=tag:Week,Values=$WEEK_TAG" "Name=instance-state-name,Values=running,stopped" \
    --query "Reservations[].Instances[].InstanceId" --output text 2>/dev/null)

if [ ! -z "$instance_ids" ]; then
    echo -e "  ${GREEN}✓${NC} EC2 인스턴스 종료: $instance_ids"
    aws ec2 terminate-instances --instance-ids $instance_ids --region $REGION 2>/dev/null || \
        echo -e "  ${RED}✗${NC} 종료 실패: $instance_ids"
else
    echo -e "  ${YELLOW}→${NC} EC2 인스턴스를 찾을 수 없습니다"
fi
echo ""

################################################################################
# 5. RDS 인스턴스 삭제
################################################################################
echo -e "${BLUE}5. RDS 인스턴스 삭제 중...${NC}"
RDS_COUNT=0

aws rds describe-db-instances --region $REGION --query "DBInstances[].DBInstanceIdentifier" --output text 2>/dev/null | \
while read -r db_instance; do
    if [ ! -z "$db_instance" ]; then
        tags=$(aws rds list-tags-for-resource \
            --resource-name arn:aws:rds:$REGION:$ACCOUNT_ID:db:$db_instance \
            --region $REGION --query "TagList[?Key=='Week' && Value=='$WEEK_TAG']" --output text 2>/dev/null)
        
        if [ ! -z "$tags" ]; then
            echo -e "  ${GREEN}✓${NC} RDS 인스턴스 삭제: $db_instance (최종 스냅샷 생략)"
            aws rds delete-db-instance \
                --db-instance-identifier $db_instance \
                --skip-final-snapshot \
                --region $REGION 2>/dev/null || \
                echo -e "  ${RED}✗${NC} 삭제 실패: $db_instance"
            RDS_COUNT=$((RDS_COUNT + 1))
        fi
    fi
done

if [ $RDS_COUNT -eq 0 ]; then
    echo -e "  ${YELLOW}→${NC} RDS 인스턴스를 찾을 수 없습니다"
fi
echo ""

################################################################################
# 6. ElastiCache 클러스터 삭제
################################################################################
echo -e "${BLUE}6. ElastiCache 클러스터 삭제 중...${NC}"
ELASTICACHE_COUNT=0

# Redis 클러스터 삭제
aws elasticache describe-cache-clusters --region $REGION --query "CacheClusters[].CacheClusterId" --output text 2>/dev/null | \
while read -r cluster; do
    if [ ! -z "$cluster" ]; then
        tags=$(aws elasticache list-tags-for-resource \
            --resource-name arn:aws:elasticache:$REGION:$ACCOUNT_ID:cluster:$cluster \
            --region $REGION --query "TagList[?Key=='Week' && Value=='$WEEK_TAG']" --output text 2>/dev/null)
        
        if [ ! -z "$tags" ]; then
            echo -e "  ${GREEN}✓${NC} ElastiCache 클러스터 삭제: $cluster"
            aws elasticache delete-cache-cluster \
                --cache-cluster-id $cluster \
                --region $REGION 2>/dev/null || \
                echo -e "  ${RED}✗${NC} 삭제 실패: $cluster"
            ELASTICACHE_COUNT=$((ELASTICACHE_COUNT + 1))
        fi
    fi
done

if [ $ELASTICACHE_COUNT -eq 0 ]; then
    echo -e "  ${YELLOW}→${NC} ElastiCache 클러스터를 찾을 수 없습니다"
fi
echo ""

################################################################################
# 7. CloudFormation 스택 삭제
################################################################################
echo -e "${BLUE}7. CloudFormation 스택 삭제 중...${NC}"
CF_COUNT=0

aws cloudformation list-stacks --region $REGION \
    --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE \
    --query "StackSummaries[].StackName" --output text 2>/dev/null | \
while read -r stack; do
    if [ ! -z "$stack" ]; then
        tags=$(aws cloudformation describe-stacks \
            --stack-name $stack \
            --region $REGION \
            --query "Stacks[0].Tags[?Key=='Week' && Value=='$WEEK_TAG']" --output text 2>/dev/null)
        
        if [ ! -z "$tags" ]; then
            echo -e "  ${GREEN}✓${NC} CloudFormation 스택 삭제: $stack"
            aws cloudformation delete-stack --stack-name $stack --region $REGION 2>/dev/null || \
                echo -e "  ${RED}✗${NC} 삭제 실패: $stack"
            CF_COUNT=$((CF_COUNT + 1))
        fi
    fi
done

if [ $CF_COUNT -eq 0 ]; then
    echo -e "  ${YELLOW}→${NC} CloudFormation 스택을 찾을 수 없습니다"
fi
echo ""

################################################################################
# 완료 메시지
################################################################################
echo -e "${GREEN}=== 리소스 삭제 완료 ===${NC}"
echo ""
echo -e "${YELLOW}참고:${NC}"
echo "- 일부 리소스는 삭제가 완료되기까지 시간이 걸릴 수 있습니다"
echo "- CloudFormation 스택 삭제는 2-5분 정도 소요됩니다"
echo "- EC2 인스턴스 종료는 1-2분 정도 소요됩니다"
echo "- RDS 인스턴스 삭제는 5-10분 정도 소요됩니다"
echo ""
echo -e "${BLUE}Tag Editor로 리소스가 모두 삭제되었는지 확인하세요:${NC}"
echo "https://console.aws.amazon.com/resource-groups/tag-editor"
echo ""
