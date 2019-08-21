def index_equals_value_search(arr):
    # for key, value in enumerate(arr):
    #  if value == key:
    #    return key
    # return -1
    # 0,  1,| 2, 3
    # -8, 0, |1, 3
    # start = 0
    #  mid
    # end arr.len-1
    # mid = (start+end)/2
    # arr[mid] == mid
    # return mid
    # arr[mid]>mid
    # modify start | end
    # arr[mid]<mid
    # modify start | end

    # 1 2 3 4 5 6 7 looking 7
    '''start <=end  // 5
    start = 6
    end = 6
    3
    mid = 6 // val = arr[3]= 4
    arr[mid]>searchVal
      end = mid - 1
    arr[mid]<searchVal //6<7
      start = mid + 1 //7
    arr[mid]==searchVal
      return true

    0    1  2  3
    [-8, 0, 2, 5]
    '''
    start = 0
    end = len(arr) - 1
    while start <= end:  ##<=
        mid = len(arr) / 2

        # Searching for the half of the array for content
        if arr[mid] == mid:
            return mid
        elif arr[mid] > mid:  ## arr[mid]=searchVal 0 mid 5 6
            start = mid + 1  ##
        elif arr[mid] < mid:
            end = mid - 1  ##
    return -1