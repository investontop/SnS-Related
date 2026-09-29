# queries.py

Pattern01 = {
    "Previous_Setups_query": """
        SELECT h.header_id id,h.stock_name, h.status, 
               h.setup_confirmed_date AS Date, 
               (COALESCE(h.exit_date, CURRENT_DATE) - h.setup_confirmed_date) AS Days,
               h.irr, h.setup_breached
        FROM public.pattern01_header h
        WHERE 1=1
        and (h.stock_name = %(stock_name)s or %(stock_name)s = '')
        and h.market = %(market)s
        and upper(h.time_frame) = upper(%(time_frame)s)
        order by h.header_id;
    """,
    "New_setup_Confirmation_insert": """
            INSERT INTO public.pattern01_header 
            (market, stock_name, setup_confirmed_date, setup_confirmed_price, time_frame, setup_breached)
            VALUES 
            (:market, :stock_name, :setup_date, :conf_price, :time_frame, :setup_breached)
            RETURNING header_id;
        """,
    "Update_setup": """
            UPDATE public.pattern01_header
            SET setup_breached = :setup_breached,
            status = case when :setup_breached = 'Yes' then 'Closed' else 'Open' end
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
            AND setup_breached = 'No'
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
            and setup_breached = 'NO';""",
    "Update_cmp_in_db_selected_records": """
            SELECT header_id, stock_name, market 
            FROM public.pattern01_header 
            WHERE market = :market 
              AND (:stock_name = '' OR stock_name = :stock_name)
              AND status = 'Open'
              AND upper(time_frame) = upper(:time_frame)
              AND setup_breached = 'No';""",
    "Update_cmp_in_db_selected_records_update": """
            UPDATE public.pattern01_header
            SET current_price = :cmp
            WHERE header_id = :header_id;
        """
}
