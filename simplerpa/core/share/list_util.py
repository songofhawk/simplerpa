def append_to(the_list, item):
    if isinstance(item, the_list):
        the_list.extend(item)
    else:
        the_list.append(item)
