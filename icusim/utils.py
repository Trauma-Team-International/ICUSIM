def _dump_dictionary_(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                print(k)
                _dump_dictionary_(v)
            else:
                print('%s : %s' % (k, v))
    elif isinstance(obj, list):
        for v in obj:
            if hasattr(v, '__iter__'):
                _dump_dictionary_(v)
            else:
                print(v)
    else:
        print(obj)
