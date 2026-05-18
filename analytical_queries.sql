-- WALL STREET DATA PIPELINE - ANALYTICAL QUERIES (ATHENA / PRESTO SQL)

-- 1. LATEST PRICES 

SELECT 
    symbol, 
    price, 
    record_time
FROM (
    SELECT 
        symbol, 
        price, 
        record_time,
        ROW_NUMBER() OVER(PARTITION BY symbol ORDER BY record_time DESC) as rn
    FROM wall_street_db.stock_prices_silver
) 
WHERE rn = 1;

-- 2. DAILY VOLATILITY & SUMMARY (Günlük Dalgalanma ve Özet)

SELECT 
    symbol,
    DATE(record_time) as trade_date,
    MIN(price) as daily_low,
    MAX(price) as daily_high,
    ROUND(AVG(price), 2) as daily_avg,
    MAX(price) - MIN(price) as daily_price_spread
FROM wall_street_db.stock_prices_silver
GROUP BY symbol, DATE(record_time)
ORDER BY trade_date DESC, daily_price_spread DESC;

-- 3. PRICE MOMENTUM USING WINDOW FUNCTIONS 

SELECT 
    symbol,
    price as current_price,
    LAG(price, 1) OVER(PARTITION BY symbol ORDER BY record_time) as previous_price,
    ROUND(price - LAG(price, 1) OVER(PARTITION BY symbol ORDER BY record_time), 2) as price_change,
    record_time
FROM wall_street_db.stock_prices_silver
ORDER BY symbol, record_time DESC;

-- 4. ALL-TIME HIGH & LOW 

SELECT 
    symbol,
    MAX(price) as highest_price,
    MIN(price) as lowest_price,
    ROUND(AVG(price), 2) as average_price,
    COUNT(*) as total_data_points
FROM wall_street_db.stock_prices_silver
GROUP BY symbol
ORDER BY highest_price DESC;
