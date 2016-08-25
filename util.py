
def seconds_to_hms(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)

    if h or (h and not m):
        return '{:02}:{:02}:{:02}'.format(h, m, s)
    else:
        return '{:02}:{:02}'.format(m, s)
