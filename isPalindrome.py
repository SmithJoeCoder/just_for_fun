class Solution:
    def isPalindrome(x):

        # """
        # :type x: int
        # :rtype: bool
        # """
        temp = str(x)[::-1]
        if str(x) == temp:
            return True
        else:
            return False
