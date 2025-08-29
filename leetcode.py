import re
import statistics


class LeetCode:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        # LeetCode Problem 1: Two Sum

        num_to_index: dict[int, int] = {}
        for idx, num in enumerate(nums):
            complement = target - num
            if complement in num_to_index:
                return [num_to_index[complement], idx]
            num_to_index[num] = idx

        return []

    def findMedianSortedArrays(self, nums1: list[int], nums2: list[int]) -> float:
        # LeetCode Problem 4: Median of Two Sorted Arrays

        return statistics.median(nums1 + nums2)

    def longestPalindrome(self, s: str) -> str:
        # LeetCode Problem 5: Longest Palindromic Substring

        def find_palindromes(input, j, k):
            palindromes = []
            while j >= 0 and k < len(input) and input[j] == input[k]:
                palindromes.append(input[j : k + 1])
                j -= 1
                k += 1
            return palindromes

        def find_palindromes_expand_from_center(input_string: str):
            palindromes = []
            for i in range(len(input_string)):
                palindromes += find_palindromes(input_string, i - 1, i + 1)
                palindromes += find_palindromes(input_string, i, i + 1)
            return palindromes

        if len(s) == 1:
            return s

        palindromes = find_palindromes_expand_from_center(s)
        try:
            return max(palindromes, key=len)
        except ValueError:
            return s[0]

    def convert(self, s: str, numRows: int) -> str:
        # LeetCode Problem 6: Zigzag Conversion

        if numRows == 1 or numRows >= len(s):
            return s

        rows = [''] * numRows
        going_down = False
        current_row = 0

        for char in s:
            rows[current_row] += char

            if current_row == 0:
                going_down = True
            elif current_row == numRows - 1:
                going_down = False

            current_row += 1 if going_down else -1

        return ''.join(rows)

    def reverse(self, x: int) -> int:
        # LeetCode Problem 7: Reverse Integer

        negative = x < 0

        input_num = str(x)[1:] if negative else str(x)
        reversed_input = int(input_num[::-1])
        if reversed_input.bit_length() > 31:
            return 0

        return -reversed_input if negative else reversed_input

    def myAtoi(self, s: str) -> int:
        # LeetCode Problem 8: String to Integer (atoi)

        int_max = 2**31 - 1
        int_min = -(2**31)

        i = 0
        n = len(s)

        while i < n and s[i] == ' ':
            i += 1

        sign = 1
        if i < n and s[i] in '-+':
            if i + 1 < n and s[i + 1] in '-+':
                return 0
            sign = -1 if s[i] == '-' else 1
            i += 1

        start = i
        while i < n and s[i].isdigit():
            i += 1
        num_str = s[start:i]
        if not num_str:
            return 0
        result = int(num_str) * sign

        return int_max if result > int_max else max(result, int_min)

    def isPalindrome(self, x: int) -> bool:
        # LeetCode Problem 9: Palindrome Number

        return str(x) == str(x)[::-1]

    def isMatch(self, s: str, p: str) -> bool:
        # LeetCode Problem 10: Regular Expression Matching

        match = re.match(p, s)

        return match[0] == s if match else False

    def intToRoman(self, num: int) -> str:
        # LeetCode Problem 12: Integer to Roman

        m = ['', 'M', 'MM', 'MMM']
        c = ['', 'C', 'CC', 'CCC', 'CD', 'D', 'DC', 'DCC', 'DCCC', 'CM']
        x = ['', 'X', 'XX', 'XXX', 'XL', 'L', 'LX', 'LXX', 'LXXX', 'XC']
        i = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX']

        return f'{m[num // 1000]}{c[(num % 1000) // 100]}{x[(num % 100) // 10]}{i[num % 10]}'

    def removeDuplicates(self, nums: list[int | str]) -> int:
        # LeetCode Problem 26: Remove Duplicates from Sorted Array

        list_length = len(nums)
        unique_values = sorted(set(nums))

        nums.clear()
        nums.extend(iter(unique_values))
        nums.extend(['_'] * (list_length - len(unique_values)))

        return len(unique_values)

    def removeElement(self, nums: list[int], val: int) -> int:
        # LeetCode Problem 27: Remove Element

        while nums.count(val) > 0:
            nums.remove(val)

        return len(nums)

    def strStr(self, haystack: str, needle: str) -> int:
        # LeetCode Problem 28: Find the Index of the First Occurrence in a String

        try:
            return haystack.index(needle)
        except ValueError:
            return -1

    def search(self, nums: list[int], target: int) -> int:
        # LeetCode Problem 33: Search in Rotated Sorted Array

        try:
            return tuple(nums).index(target)
        except ValueError:
            return -1

    def findMin(self, nums: list[int]) -> int:
        # LeetCode Problem 153: Find Minimum in Rotated Sorted Array

        return min(tuple(nums))

    def containsDuplicate(self, nums: list[int]) -> bool:
        # LeetCode Problem 217: Contains Duplicate

        return len(nums) != len(set(nums))


def run_leetcode_tests() -> None:
    lc = LeetCode()

    # Problem 1: Two Sum
    assert lc.twoSum([2, 7, 11, 15], 9) == [0, 1]
    assert lc.twoSum([3, 2, 4], 6) == [1, 2]
    assert lc.twoSum([3, 3], 6) == [0, 1]

    # Problem 4: Median of Two Sorted Arrays
    assert lc.findMedianSortedArrays([1, 3], [2]) == 2.0
    assert lc.findMedianSortedArrays([1, 2], [3, 4]) == 2.5

    # Problem 5: Longest Palindromic Substring
    assert lc.longestPalindrome('babad') in ['bab', 'aba']
    assert lc.longestPalindrome('cbbd') == 'bb'

    # Problem 6: Zigzag Conversion
    assert lc.convert('PAYPALISHIRING', 3) == 'PAHNAPLSIIGYIR'
    assert lc.convert('PAYPALISHIRING', 4) == 'PINALSIGYAHRPI'
    assert lc.convert('A', 1) == 'A'

    # Problem 7: Reverse Integer
    assert lc.reverse(123) == 321
    assert lc.reverse(-123) == -321
    assert lc.reverse(120) == 21

    # Problem 8: String to Integer (atoi)
    assert lc.myAtoi('42') == 42
    assert lc.myAtoi('   -42') == -42
    assert lc.myAtoi('1337c0d3') == 1337
    assert lc.myAtoi('0-1') == 0
    assert lc.myAtoi('words and 987') == 0
    assert lc.myAtoi('-+12') == 0

    # Problem 9: Palindrome Number
    assert lc.isPalindrome(121) is True
    assert lc.isPalindrome(-121) is False
    assert lc.isPalindrome(10) is False

    # Problem 10: Regular Expression Matching
    assert lc.isMatch('aa', 'a') is False
    assert lc.isMatch('aa', 'a*') is True
    assert lc.isMatch('ab', '.*') is True

    # Problem 12: Integer to Roman
    assert lc.intToRoman(3749) == 'MMMDCCXLIX'
    assert lc.intToRoman(58) == 'LVIII'
    assert lc.intToRoman(1994) == 'MCMXCIV'

    # Problem 26: Remove Duplicates from Sorted Array
    assert lc.removeDuplicates([1, 1, 2]) == 2
    assert lc.removeDuplicates([0, 0, 1, 1, 2, 2, 3, 3, 4]) == 5

    # Problem 27: Remove Element
    assert lc.removeElement([3, 2, 2, 3], 3) == 2
    assert lc.removeElement([0, 1, 2, 2, 3, 0, 4, 2], 2) == 5

    # Problem 28: Find the Index of the First Occurrence in a String
    assert lc.strStr('sadbutsad', 'sad') == 0
    assert lc.strStr('leetcode', 'leeto') == -1

    # Problem 33: Search in Rotated Sorted Array
    assert lc.search([4, 5, 6, 7, 0, 1, 2], 0) == 4
    assert lc.search([4, 5, 6, 7, 0, 1, 2], 3) == -1
    assert lc.search([1], 0) == -1

    # Problem 153: Find Minimum in Rotated Sorted Array
    assert lc.findMin([3, 4, 5, 1, 2]) == 1
    assert lc.findMin([4, 5, 6, 7, 0, 1, 2]) == 0
    assert lc.findMin([11, 13, 15, 17]) == 11

    # Problem 217: Contains Duplicate
    assert lc.containsDuplicate([1, 2, 3, 1]) is True
    assert lc.containsDuplicate([1, 2, 3, 4]) is False
    assert lc.containsDuplicate([1, 1, 1, 1]) is True


if __name__ == '__main__':
    run_leetcode_tests()
