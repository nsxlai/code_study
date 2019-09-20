def twoSum(nums, target):
    temp_dict = {}
    for i in range(len(nums)):
        complement = target - nums[i]
        print(f'temp_dict = {temp_dict}')
        print(f'complement = {complement}')
        if complement in temp_dict and temp_dict[complement] != i:
            return sorted([i, temp_dict[complement]])
        else:
            temp_dict[nums[i]] = i


if __name__ == '__main__':
    nums = [3, 2, 4]
    target = 6
    print(twoSum(nums, target))