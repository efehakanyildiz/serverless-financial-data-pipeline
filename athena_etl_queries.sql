-- ==============================================================================
-- MEDALLION ARCHITECTURE: BRONZE TO SILVER TRANSFORMATION (AWS ATHENA)
-- ==============================================================================

-- 1. Initial Transformation: Raw JSON to Compressed Parquet (CTAS)
-- This query creates the Silver table and optimizes the data format.
CREATE TABLE wall_street_db.stock_prices_silver
WITH (
    format = 'PARQUET',
    external_location = 's3://wall-street-silver-efe/'
) AS 
SELECT 
    symbol, 
    price, 
    CAST(from_iso8601_timestamp(timestamp) AS timestamp) as record_time
FROM wall_street_db.stock_prices_raw;


-- 2. Incremental Load (Scheduled via AWS Step Functions)
-- This query only inserts new records, preventing data duplication.
INSERT INTO wall_street_db.stock_prices_silver
SELECT 
    symbol, 
    price, 
    CAST(from_iso8601_timestamp(timestamp) AS timestamp)
FROM wall_street_db.stock_prices_raw
WHERE CAST(from_iso8601_timestamp(timestamp) AS timestamp) > (
    SELECT COALESCE(MAX(record_time), timestamp '1970-01-01') 
    FROM wall_street_db.stock_prices_silver
);
