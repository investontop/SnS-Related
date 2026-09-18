# queries.py

Pattern01 = {
    "Previous_Setups": """
        SELECT h.stock_name, h.setup_confirmed_date AS Date, 
               h.setup_confirmed_price AS Price,
               h.status, h.irr
        FROM public.pattern01_header h
        WHERE stock_name = %(stock_name)s
    """
}
