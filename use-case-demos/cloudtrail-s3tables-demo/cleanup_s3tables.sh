#!/bin/bash

# --- INITIALIZE VARIABLES ---
REGION=""
BUCKET_ARN=""
NAMESPACE=""

# --- USAGE HELPER ---
usage() {
    echo "Error: Missing arguments."
    echo "Usage: $0 --region <region> --table-bucket-arn <arn> --namespace <namespace>"
    echo ""
    echo "Example:"
    echo "  $0 --region us-east-1 \\"
    echo "     --table-bucket-arn arn:aws:s3tables:us-east-1:123456:bucket/my-bucket \\"
    echo "     --namespace my_data"
    exit 1
}

# --- ARGUMENT PARSING ---
while [[ $# -gt 0 ]]; do
    case $1 in
        --region) REGION="$2"; shift 2 ;;
        --table-bucket-arn) BUCKET_ARN="$2"; shift 2 ;;
        --namespace) NAMESPACE="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

# --- STRICT VALIDATION ---
if [[ -z "$REGION" ]] || [[ -z "$BUCKET_ARN" ]] || [[ -z "$NAMESPACE" ]]; then
    usage
fi

echo "===================================================="
echo "S3 TABLES DESTRUCTION SCRIPT"
echo "===================================================="
echo "Region:        $REGION"
echo "Target Bucket: $BUCKET_ARN"
echo "Namespace:     $NAMESPACE"
echo "===================================================="

# --- STAGE 1: DELETE TABLES ---
echo "Checking for tables in [$NAMESPACE]..."
TABLES=$(aws s3tables list-tables \
    --region "$REGION" \
    --table-bucket-arn "$BUCKET_ARN" \
    --namespace "$NAMESPACE" \
    --query 'tables[].name' \
    --output text)

if [ -z "$TABLES" ] || [ "$TABLES" == "None" ]; then
    echo "No tables found in namespace [$NAMESPACE]."
else
    echo "The following tables will be PERMANENTLY DELETED:"
    echo "$TABLES" | tr '\t' '\n'
    read -p "Delete these $(echo $TABLES | wc -w) table(s)? (y/N): " CONFIRM_TABLES
    if [[ "$CONFIRM_TABLES" =~ ^[Yy]$ ]]; then
        for table in $TABLES; do
            echo -n "Deleting table [$table]... "
            aws s3tables delete-table --region "$REGION" --table-bucket-arn "$BUCKET_ARN" --namespace "$NAMESPACE" --name "$table"
            echo "DONE"
        done
    else
        echo "Table deletion skipped."
    fi
fi

echo "----------------------------------------------------"

# --- STAGE 2: DELETE NAMESPACE ---
read -p "Delete the Namespace [$NAMESPACE]? (Note: Must be empty) (y/N): " CONFIRM_NS
if [[ "$CONFIRM_NS" =~ ^[Yy]$ ]]; then
    echo -n "Deleting Namespace [$NAMESPACE]... "
    aws s3tables delete-namespace --region "$REGION" --table-bucket-arn "$BUCKET_ARN" --namespace "$NAMESPACE"
    if [ $? -eq 0 ]; then echo "SUCCESS"; else echo "FAILED"; exit 1; fi
else
    echo "Namespace deletion skipped. Cannot proceed to delete bucket."
    exit 0
fi

echo "----------------------------------------------------"

# --- STAGE 3: DELETE TABLE BUCKET ---
read -p "CRITICAL: Delete the entire Table Bucket [$BUCKET_ARN]? (y/N): " CONFIRM_BUCKET
if [[ "$CONFIRM_BUCKET" =~ ^[Yy]$ ]]; then
    echo -n "Deleting Table Bucket... "
    aws s3tables delete-table-bucket --region "$REGION" --table-bucket-arn "$BUCKET_ARN"
    if [ $? -eq 0 ]; then echo "SUCCESS"; else echo "FAILED"; exit 1; fi
else
    echo "Bucket deletion skipped."
fi

echo "===================================================="
echo "All requested operations completed."