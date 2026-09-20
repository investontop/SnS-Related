# queries.py

Pattern01 = {
    "Previous_Setups_query": """
        SELECT h.header_id id,h.stock_name, h.status, 
               h.setup_confirmed_date AS Date, 
               (h.setup_confirmed_date - h.exit_date) AS Days,
               h.irr, h.setup_breached
        FROM public.pattern01_header h
        WHERE 1=1
        and (h.stock_name = %(stock_name)s or %(stock_name)s = '')
        and h.market = %(market)s
        order by h.header_id;
    """,
    "New_setup_Confirmation_insert": """
            INSERT INTO public.pattern01_header 
            (market, stock_name, setup_confirmed_date, setup_confirmed_price, setup_breached)
            VALUES 
            (:market, :stock_name, :setup_date, :conf_price, :setup_breached)
            RETURNING header_id;
        """,
    "Update_setup": """
            UPDATE public.pattern01_header
            SET setup_breached = :setup_breached
            WHERE header_id = :header_id;
        """,
    "Delete_selected_records": """
            DELETE FROM public.pattern01_header
            WHERE header_id = ANY(:header_ids);
        """,
    # "Search_stock_names": """
    #         SELECT DISTINCT stock_name
    #         FROM public.pattern01_header
    #         WHERE stock_name ILIKE :stock_name_pattern
    #         and market = :market
    #         and setup_breached = 'NO';
    #     """,
    "Get_stock_lookup": """
            SELECT DISTINCT header_id, stock_name
            FROM public.pattern01_header
            WHERE stock_name ILIKE %(stock_name_pattern)s
            AND market = %(market)s
            AND setup_breached = 'NO'
            order by stock_name, header_id;
            """,
    "Setup_Entry_Header_update": """
            UPDATE public.pattern01_header
            SET purchased_qty = purchased_qty + :qty,
                invested_amount = invested_amount + (:qty * :price),
                avg_price = (invested_amount + (:qty * :price)) / (purchased_qty + :qty)
            WHERE stock_name = :stock
            and market = :market
            and header_id = :header_id
            and setup_breached = 'NO';"""
}
