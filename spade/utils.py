import warnings


def deprecated(new_func, old_func):
    def wrapper(*args, **kwargs):
        message = 'Call to deprecated function "{}". Use function "{}" instead.'.format(
            old_func,
            new_func.__name__)

        warnings.simplefilter('always', PendingDeprecationWarning)  # turn off filter
        warnings.warn(message,
                      category=PendingDeprecationWarning, stacklevel=2)
        warnings.simplefilter('default', PendingDeprecationWarning)  # reset filter

        return new_func(*args, **kwargs)

    return wrapper