TABLES = ["transactions", "token_transfers"]

SOURCE_BUCKET = "aws-public-blockchain"
TARGET_BUCKET = "aws-web3-eth-demo"
TARGET_DB     = "eth_iceberg"

DATE_START = "2026-01-02"
DATE_END   = "2026-01-02"

# Schemas from https://github.com/aws-solutions-library-samples/guidance-for-digital-assets-on-aws
ETH_SCHEMAS = {
    "blocks": """
        `date`               STRING,
        `timestamp`          TIMESTAMP,
        `number`             BIGINT,
        `hash`               STRING,
        `parent_hash`        STRING,
        `nonce`              STRING,
        `sha3_uncles`        STRING,
        `logs_bloom`         STRING,
        `transactions_root`  STRING,
        `state_root`         STRING,
        `receipts_root`      STRING,
        `miner`              STRING,
        `difficulty`         DOUBLE,
        `total_difficulty`   DOUBLE,
        `size`               BIGINT,
        `extra_data`         STRING,
        `gas_limit`          BIGINT,
        `gas_used`           BIGINT,
        `transaction_count`  BIGINT,
        `base_fee_per_gas`   BIGINT
    """,
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
    "logs": """
        `date`               STRING,
        `log_index`          BIGINT,
        `transaction_hash`   STRING,
        `transaction_index`  BIGINT,
        `address`            STRING,
        `data`               STRING,
        `topics`             ARRAY<STRING>,
        `block_timestamp`    TIMESTAMP,
        `block_number`       BIGINT,
        `block_hash`         STRING
    """,
    "traces": """
        `date`               STRING,
        `transaction_hash`   STRING,
        `transaction_index`  BIGINT,
        `from_address`       STRING,
        `to_address`         STRING,
        `value`              DOUBLE,
        `input`              STRING,
        `output`             STRING,
        `trace_type`         STRING,
        `call_type`          STRING,
        `reward_type`        STRING,
        `gas`                BIGINT,
        `gas_used`           BIGINT,
        `subtraces`          BIGINT,
        `trace_address`      STRING,
        `error`              STRING,
        `status`             BIGINT,
        `block_timestamp`    TIMESTAMP,
        `block_number`       BIGINT,
        `block_hash`         STRING,
        `trace_id`           STRING
    """,
    "contracts": """
        `date`               STRING,
        `address`            STRING,
        `bytecode`           STRING,
        `block_timestamp`    TIMESTAMP,
        `block_number`       BIGINT,
        `block_hash`         STRING
    """,
}
