class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        dict = {}
        # Convert the user input from list to dictionary
        for key, value in enumerate(nums):
            dict[key] = value
        for key_num, value_num in enumerate(nums):
            complement = target - value_num
            for key_dict, value_dict in dict.items():
                if value_dict == complement:
                    if (complement in dict.values()) and (key_num != key_dict):                
                        return [key_num, key_dict]
        else:
            raise ValueError('There is no value matching')