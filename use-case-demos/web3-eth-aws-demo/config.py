import os

TABLES = ["transactions", "token_transfers"]

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
SOURCE_BUCKET = "aws-public-blockchain"
TARGET_BUCKET = os.environ.get("TARGET_BUCKET", "aws-web3-eth-demo")
TARGET_DB = os.environ.get("TARGET_DB", "eth_iceberg")

DATE_START = os.environ.get("DATE_START", "2026-01-01")
DATE_END = os.environ.get("DATE_END", "2026-01-01")

# Schemas from https://github.com/aws-solutions-library-samples/guidance-for-digital-assets-on-aws
ETH_SCHEMAS = {
    "transactions": """
        `date`                          STRING,
        `hash`                          STRING,
        `nonce`                         BIGINT,
        `transaction_index`             BIGINT,
        `from_address`                  STRING,
        `to_address`                    STRING,
        `value`                         DOUBLE,
        `gas`                           BIGINT,
        `gas_price`                     BIGINT,
        `input`                         STRING,
        `receipt_cumulative_gas_used`   BIGINT,
        `receipt_gas_used`              BIGINT,
        `receipt_contract_address`      STRING,
        `receipt_status`                BIGINT,
        `block_timestamp`               TIMESTAMP,
        `block_number`                  BIGINT,
        `block_hash`                    STRING,
        `max_fee_per_gas`               BIGINT,
        `max_priority_fee_per_gas`      BIGINT,
        `transaction_type`              BIGINT,
        `receipt_effective_gas_price`   BIGINT
    """,
    "token_transfers": """
        `date`               STRING,
        `token_address`      STRING,
        `from_address`       STRING,
        `to_address`         STRING,
        `value`              DOUBLE,
        `transaction_hash`   STRING,
        `log_index`          BIGINT,
        `block_timestamp`    TIMESTAMP,
        `block_number`       BIGINT,
        `block_hash`         STRING
    """,
}
