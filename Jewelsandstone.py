class Solution:
    def numJewelsInStones(J, S):
        count = 0
        for i in S:
            if i in J:
                count += 1
        print(count)
        # """
        # :type J: str
        # :type S: str
        # :rtype: int
        # """


J = "aA"
S = "aAAbbbb"
Solution.numJewelsInStones(J, S)