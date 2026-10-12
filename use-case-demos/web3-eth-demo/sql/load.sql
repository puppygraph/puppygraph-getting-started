CREATE DATABASE IF NOT EXISTS eth_iceberg;

CREATE TABLE eth_iceberg.transactions (
    `date` STRING,
    `hash` STRING,
    `nonce` BIGINT,
    `transaction_index` BIGINT,
    `from_address` STRING,
    `to_address` STRING,
    `value` DOUBLE,
    `gas` BIGINT,
    `gas_price` BIGINT,
    `input` STRING,
    `receipt_cumulative_gas_used` BIGINT,
    `receipt_gas_used` BIGINT,
    `receipt_contract_address` STRING,
    `receipt_status` BIGINT,
    `block_timestamp` TIMESTAMP,
    `block_number` BIGINT,
    `block_hash` STRING,
    `max_fee_per_gas` BIGINT,
    `max_priority_fee_per_gas` BIGINT,
    `transaction_type` BIGINT,
    `receipt_effective_gas_price` BIGINT
) USING iceberg;
INSERT INTO eth_iceberg.transactions
SELECT
    CAST(date AS STRING),
    hash,
    nonce,
    transaction_index,
    from_address,
    to_address,
    value,
    gas,
    gas_price,
    input,
    receipt_cumulative_gas_used,
    receipt_gas_used,
    receipt_contract_address,
    receipt_status,
    block_timestamp,
    block_number,
    block_hash,
    max_fee_per_gas,
    max_priority_fee_per_gas,
    transaction_type,
    receipt_effective_gas_price
FROM parquet.`/parquet_data/transactions`;

CREATE TABLE eth_iceberg.token_transfers (
    `date` STRING,
    `token_address` STRING,
    `from_address` STRING,
    `to_address` STRING,
    `value` DOUBLE,
    `transaction_hash` STRING,
    `log_index` BIGINT,
    `block_timestamp` TIMESTAMP,
    `block_number` BIGINT,
    `block_hash` STRING
) USING iceberg;
INSERT INTO eth_iceberg.token_transfers
SELECT
    CAST(date AS STRING),
    token_address,
    from_address,
    to_address,
    value,
    transaction_hash,
    log_index,
    block_timestamp,
    block_number,
    block_hash
FROM parquet.`/parquet_data/token_transfers`;
