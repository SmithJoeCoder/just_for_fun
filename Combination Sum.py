class Solution:
    def combinationSum(candidates, target):
        result = list
        if target in candidates:
            result.append(target)
        print(result)
        # """
        # :type candidates: List[int]
        # :type target: int
        # :rtype: List[List[int]]
        # """

candidates = [2, 3, 6, 7]
Solution.combinationSum(candidates, 7)