# Palindrome Number

- **Platform:** LeetCode
- **Difficulty:** Easy
- **Tags:** Math
- **Link:** https://leetcode.com/problems/palindrome-number/
- **Language (detected):** python3
- **Runtime:** 4 ms
- **Memory:** 19.4 MB

## Problem (summary)

Given an integer x, return true if x is a palindrome, and false otherwise.

 

Example 1:

Input: x = 121
Output: true
Explanation: 121 reads as 121 from left to right and from right to left.

Example 2:

Input: x = -121
Output: false
Explanation: From left to right, it reads -121. From right to left, it becomes 121-. Therefore it is not a palindrome.

Example 3:

Input: x = 10
Output: false
Explanation: Reads 01 from right to left. Therefore it is not a palindrome.

 

Constraints:

	- -231 31 - 1

 

Follow up: Could you solve it without converting the integer to a string?

## Approach

**Approach**
1. If the integer `x` is negative, it cannot be a palindrome (the minus sign would only appear on the left side), so return `False` immediately.
2. Convert the integer to its decimal string representation using `str(x)`.
3. Create the reversed version of that string with slicing `[::-1]`.
4. Compare the original string with the reversed string. If they are identical, the number reads the same forward and backward, so return `True`; otherwise return `False`.

The solution follows the straightforward *string‑compare* technique, which satisfies the problem statement but does not meet the follow‑up requirement of O(1) extra space.

## Complexity

- **Time:** O(n) where n is the number of digits in x (string length)
- **Space:** O(n) for the string representation and its reversed copy

## Pros

- Very concise and easy to understand
- Leverages Python’s built‑in string reversal which is highly optimized
- Handles all positive integers correctly without extra arithmetic

## Cons

- Uses O(n) extra space, violating the follow‑up constraint of O(1) space
- Relies on string conversion, which may be considered cheating in an interview setting
- Performance may be slightly slower than a pure arithmetic solution for very large inputs

## Edge cases

- Negative numbers (e.g., -121) should immediately return false
- Numbers that end with 0 but are not 0 themselves (e.g., 10, 100) are not palindromes
- Single‑digit numbers (including 0) are always palindromes
- Maximum 32‑bit signed integer value (2^31‑1) should be handled without overflow because Python ints are unbounded
