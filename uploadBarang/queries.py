from datetime import date

def get_date():
    today = date.today()
    return today.strftime("%Y-%m-%d")

def input_verification_ktp_docs_to_db(username, ktp_file_name, selfie_file_name, seller_verification_id):
    query = """
        INSERT INTO
        
        seller_verification_documents 
        (id, seller_username, path_ktp, path_selfie, notes, verification_status_id)
        
        VALUES
        ('{}', '{}', '{}', '{}', '{}', '{}')
    """.format(
        seller_verification_id, 
        username, 
        ktp_file_name,
        selfie_file_name,
        "",
        "fe2caca5-be86-45b1-997e-5a7a2bcf2a6e"
    )

    query_update_user = f"""
        UPDATE  auth_user
        SET     date_seller = '{get_date()}'
        WHERE   username = '{username}';
    """

    return query, query_update_user

def input_verification_listing_docs_to_db(username, listing_id, pdf_filename, event_id, listing_verification_id):
    query_listing = """
        INSERT INTO

        listing
        (id, seller_username, date_created, is_sold, is_public, is_verified, event_id)

        VALUES
        ('{}', '{}', '{}', '{}', '{}', '{}', '{}')
    """.format(
        listing_id,
        username,
        get_date(),
        "false",
        "false",
        "false",
        event_id
    )

    query_listing_document = """
        INSERT INTO

        listing_verification_documents
        (id, path_pdf, notes, listing_id, verification_status_id)

        VALUES
        ('{}', '{}', '{}', '{}', '{}')
    """.format(
        listing_verification_id,
        pdf_filename,
        "",
        listing_id,
        "fe2caca5-be86-45b1-997e-5a7a2bcf2a6e"
    )
    return query_listing, query_listing_document

def get_events():
    query = """
        SELECT  title || ' [' || category || ']'
        FROM    events;
    """

    return query

def get_event_id(title, category):
    query = """
        SELECT  id
        FROM    events
        WHERE   title = '{}'
                AND category = '{}'
    """.format(title, category)

    return query