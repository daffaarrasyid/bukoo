def haha(h):
    if h == 0:
        return 1
    else:
        return h%10 * haha(h/10)
    
print(haha(191963))
    