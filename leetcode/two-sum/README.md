# Two Sum

- **Platform:** LeetCode
- **Difficulty:** Easy
- **Tags:** Array, Hash Table
- **Link:** https://leetcode.com/problems/two-sum/
- **Language (detected):** python3
- **Runtime:** 450 ms
- **Memory:** 19.8 MB

## Problem (summary)

Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.

 

Example 1:

Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].

Example 2:

Input: nums = [3,2,4], target = 6
Output: [1,2]

Example 3:

Input: nums = [3,3], target = 6
Output: [0,1]

 

Constraints:

	- 2 4

	- -109 9

	- -109 9

	- Only one valid answer exists.

 

Follow-up: Can you come up with an algorithm that is less than O(n2) time complexity?

## Approach

### Approach
The provided solution iterates over each element `i` in `nums` and checks whether the complementary value `target - nums[i]` exists somewhere in the array. It uses Python’s `in` operator to test existence and `list.index` to retrieve the first index of that complement. If the found index is different from `i`, the pair `[i, complement_index]` is returned.

**Why it works**
- The problem guarantees exactly one valid pair, so the first time we encounter a matching complement we can safely return it.
- The `!= i` guard ensures we never use the same element twice, handling the case where the complement equals the current element.

**Step‑by‑step**
1. Loop `i` from `0` to `len(nums)-1`.
2. Compute `need = target - nums[i]`.
3. If `need` is present in `nums` **and** the first occurrence of `need` is not at position `i`, return `[i, nums.index(need)]`.

While correct, this approach repeatedly scans the list for each element, leading to a quadratic runtime.

**Typical optimal solution (for reference)**
A linear‑time solution uses a hash map (`dict`) that stores each number’s index while iterating once through the array. For each `num`, we check if `target - num` is already in the map; if so, we return the stored index and the current index.

---

## Complexity

- **Time:** O(n^2) – each iteration performs an `in` check and an `index` call, both O(n).
- **Space:** O(1) extra space (ignoring input storage).

## Pros

- Very concise and easy to read.
- Uses only built‑in list operations; no extra data structures needed.
- Correct for all inputs that satisfy the problem’s guarantees.

## Cons

- Quadratic time makes it unsuitable for large arrays (e.g., n > 10⁴).
- Repeated linear scans (`in` and `index`) cause unnecessary overhead.
- Relies on `list.index`, which always returns the first occurrence; this works here because of the `!= i` check, but can be confusing.
- Does not exploit the optimal O(n) hash‑map technique.

## Edge cases

- Array contains duplicate numbers (e.g., [3,3] with target 6).
- Complement equals the current element but appears elsewhere (e.g., [1,2,3,4] target 2).
- Negative numbers and large magnitude values.
- Minimum length array of size 2.
- Very large input size where O(n^2) would time out.
