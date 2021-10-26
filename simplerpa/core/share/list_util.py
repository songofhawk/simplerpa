def append_to(the_list, item):
    if isinstance(item, list):
        the_list.extend(item)
    elif item is None:
        return
    else:
        the_list.append(item)
