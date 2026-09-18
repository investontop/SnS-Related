-- 1. Create Parent Table: Pattern01_Header
CREATE TABLE Pattern01_Header (
    header_id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    market              VARCHAR(10) NOT NULL CHECK (market IN ('USA', 'INDIA')),
    stock_name          VARCHAR(50) NOT NULL,
    setup_confirmed_date DATE NOT NULL,
    setup_confirmed_price NUMERIC(12, 4) NOT NULL,
    status              VARCHAR(10) NOT NULL DEFAULT 'Open' CHECK (status IN ('Open', 'Closed')),
    purchased_qty       NUMERIC(12, 4) DEFAULT 0,
    invested_amount     NUMERIC(14, 2) DEFAULT 0.00,
    exit_date           DATE,
    exit_price          NUMERIC(12, 4),
    profit_loss         NUMERIC(14, 2),
    irr                 NUMERIC(8, 4), -- Store IRR as a percentage (e.g., 12.5000 = 12.5%)
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure unique constraint on market + stock_name if you only allow one open position per stock
    CONSTRAINT uq_header_key UNIQUE (header_id)
);

-- 2. Create Child Table: Pattern01_Line
CREATE TABLE Pattern01_Line (
    line_id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    header_id           BIGINT NOT NULL,
    trade_type          VARCHAR(10) NOT NULL CHECK (trade_type IN ('BUY', 'SELL')),
    trade_date          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    quantity            NUMERIC(12, 4) NOT NULL CHECK (quantity > 0),
    price               NUMERIC(12, 4) NOT NULL CHECK (price > 0),
    trade_amount        NUMERIC(14, 2) GENERATED ALWAYS AS (quantity * price) STORED,
    notes               TEXT,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Key linkage back to Header
    CONSTRAINT fk_line_header 
        FOREIGN KEY (header_id) 
        REFERENCES Pattern01_Header (header_id) 
        ON DELETE CASCADE
);

-- 3. Index for fast performance on child lookups
CREATE INDEX idx_pattern01_line_header ON Pattern01_Line(header_id);