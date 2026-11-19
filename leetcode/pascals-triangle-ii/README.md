# Pascal's Triangle II

- **Platform:** LeetCode
- **Difficulty:** Easy
- **Tags:** Array, Dynamic Programming
- **Link:** https://leetcode.com/problems/pascals-triangle-ii/
- **Language (detected):** python3
- **Runtime:** 1 ms
- **Memory:** 19.2 MB

## Problem (summary)

Given an integer rowIndex, return the rowIndexth (0-indexed) row of the Pascal's triangle.

In Pascal's triangle, each number is the sum of the two numbers directly above it as shown:

 

Example 1:

Input: rowIndex = 3
Output: [1,3,3,1]
Example 2:

Input: rowIndex = 0
Output: [1]
Example 3:

Input: rowIndex = 1
Output: [1,1]

 

Constraints:

	- 0 

 

Follow up: Could you optimize your algorithm to use only O(rowIndex) extra space?

## Approach

**Approach**

The solution builds Pascal’s triangle row‑by‑row, keeping only the most recent row in memory.
1. Start with the first row `[1]`.
2. For each subsequent row (from `0` to `rowIndex‑1`):
   * Create a new temporary list `tempList` of length `len(prevRow)+1`.
   * For each position `j` in the new row, the value is the sum of the two numbers directly above it:
     * `front = prevRow[j‑1]` if `j > 0` else `0`.
     * `end   = prevRow[j]`   if `j < len(prevRow)` else `0`.
   * Append `front + end` to `tempList`.
   * Replace `prevRow` with `tempList`.
3. After the loop finishes, `prevRow` holds the desired `rowIndex`‑th row and is returned.

The algorithm uses only one list that grows to size `rowIndex+1`, satisfying the follow‑up requirement of **O(rowIndex)** extra space.

---
**Why it works**

Each element of Pascal’s triangle is defined as the sum of the two elements directly above it. By iterating over the previous row and explicitly handling the “virtual” zeros at the boundaries (`front` and `end`), we correctly compute every entry of the next row. Repeating this process `rowIndex` times yields exactly the `rowIndex`‑th row.

## Complexity

- **Time:** O(rowIndex^2)
- **Space:** O(rowIndex)

## Pros

- Very easy to understand and implement
- Uses only O(rowIndex) additional space as required by the follow‑up
- Works for all valid inputs without special‑case handling

## Cons

- Time complexity is quadratic; a more optimal O(rowIndex) solution exists using in‑place updates or combinatorial formula
- Creates a new list on each iteration, which incurs extra allocation overhead

## Edge cases

- rowIndex = 0 (should return [1])
- rowIndex = 1 (should return [1,1])
- Maximum allowed rowIndex (still fits within memory because only O(rowIndex) space is used)
