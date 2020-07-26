class Solution:
    ''' DEBUG version
    def longestPalindrome(self, s: str) -> str:
        palindrome = ''

        for i in range(len(s)):
            # Case1: palindrome string length has odd count; e.g., 'ABCBA'
            print('-' * 20)
            print(f'i = {i}')
            print('case1...')
            temp = self.getlongestpalindrome(s, i, i)
            len1 = len(temp)
            print(f'len1 = {len1}; temp = {temp}')
            if len1 > len(palindrome):
                palindrome = temp
                print(f'palindrom1 = {palindrome}')

            # Case2: palindrome string length has even count; e.g., 'BB'
            print('case2...')
            temp = self.getlongestpalindrome(s, i, i+1)
            len2 = len(temp)
            print(f'len2 = {len2}; temp = {temp}')
            if len2 > len(palindrome):
                palindrome = temp
                print(f'palindrom2 = {palindrome}')

        return palindrome
        '''

    def longestPalindrome(self, s: str) -> str:
        palindrome = ''
        for i in range(len(s)):
            # Case1: palindrome string length has odd count; e.g., 'ABCBA'
            temp = self.getlongestpalindrome(s, i, i)
            if len(temp) > len(palindrome):
                palindrome = temp

            # Case2: palindrome string length has even count; e.g., 'BB'
            temp = self.getlongestpalindrome(s, i, i + 1)
            if len(temp) > len(palindrome):
                palindrome = temp
        return palindrome

    def getlongestpalindrome(self, s, l, r):
        while l >= 0 and r < len(s) and s[l] == s[r]:
            l -= 1
            r += 1
        return s[l + 1:r]


if __name__ == '__main__':
    s = Solution()
    pal1 = s.longestPalindrome('abbacababba')
    print(f'palindrom substring = {pal1}')
    print('=' * 30)
    pal2 = s.longestPalindrome('babad')
    print(f'palindrom substring = {pal2}')
