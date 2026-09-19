# queries.py

Pattern01 = {
    "Previous_Setups_query": """
        SELECT h.header_id id,h.stock_name, h.status, 
               h.setup_confirmed_date AS Date, 
               (h.setup_confirmed_date - h.exit_date) AS Days,
               h.irr, h.setup_breached
        FROM public.pattern01_header h
        WHERE stock_name = %(stock_name)s
        and h.market = %(market)s
    """,
    "New_setup_Confirmation_insert": """
            INSERT INTO public.pattern01_header 
            (market, stock_name, setup_confirmed_date, setup_confirmed_price, setup_breached)
            VALUES 
            (:market, :stock_name, :setup_date, :conf_price, :setup_breached)
            RETURNING header_id;
        """
}
