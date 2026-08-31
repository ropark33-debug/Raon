def find_max_idx(a)
    n = len(a)
    
    max_idx = 0
    for i in range(1, n):
        if a[i] > a[max_idx]:
            max_idx = i
    return max_idx

v = [3, 1, 4, 1, 5, 9, 2, 6, 5]
print(find_max_idx(v))