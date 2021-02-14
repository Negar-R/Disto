def pagination(list_of_obj, per_page_limit):
    list_length = len(list_of_obj)
    if list_length == per_page_limit:
        has_continue = True
    else:
        has_continue = False
    if list_length:
        start_id = list_of_obj[-1]['_id']
    else:
        start_id = None
    return start_id, has_continue
