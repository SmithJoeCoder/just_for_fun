class Solution:

    def twoSum(nums, target):
        look_for = {}
        for n, x in enumerate(nums, 0):
            try:
                return look_for[x], n
            except KeyError:
                look_for.setdefault(target - x, n)
        # """
        # :type nums: List[int]
        # :type target: int
        # :rtype: List[int]
        # """


nums_list = [2, 7, 11, 15]
target = 9
result = Solution.twoSum(nums_list, target)
print(result)
