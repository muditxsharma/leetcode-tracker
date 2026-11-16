# Find Customer Referee

- **Platform:** LeetCode
- **Difficulty:** Easy
- **Tags:** Database
- **Link:** https://leetcode.com/problems/find-customer-referee/
- **Language (detected):** mysql
- **Runtime:** 466 ms
- **Memory:** 0B

## Problem (summary)

Table: Customer

+-------------+---------+
| Column Name | Type    |
+-------------+---------+
| id          | int     |
| name        | varchar |
| referee_id  | int     |
+-------------+---------+
In SQL, id is the primary key column for this table.
Each row of this table indicates the id of a customer, their name, and the id of the customer who referred them.

 

Find the names of the customer that are either:

	- referred by any customer with id != 2.

	- not referred by any customer.

Return the result table in any order.

The result format is in the following example.

 

Example 1:

Input: 
Customer table:
+----+------+------------+
| id | name | referee_id |
+----+------+------------+
| 1  | Will | null       |
| 2  | Jane | null       |
| 3  | Alex | 2          |
| 4  | Bill | null       |
| 5  | Zack | 1          |
| 6  | Mark | 2          |
+----+------+------------+
Output: 
+------+
| name |
+------+
| Will |
| Jane |
| Bill |
| Zack |
+------+

## Approach

### Approach
1. **Interpret the requirement** – We need the names of customers who are either:
   - Referred by a customer whose `id` is **not** `2`.
   - Not referred by anyone (`referee_id` is `NULL`).
2. **SQL filtering** – A single `WHERE` clause can capture both conditions:
   - `referee_id IS NULL` handles the “not referred” case.
   - `referee_id <> 2` handles the “referred by someone other than id 2” case.
3. **Compact expression** – The provided solution uses `COALESCE(referee_id, 0) != 2`. `COALESCE` replaces `NULL` with `0`, and because `0 != 2`, rows with `NULL` also satisfy the predicate.
4. **Select the name column** – Finally, return only the `name` column as required.

**SQL Query**
```sql
SELECT name
FROM Customer
WHERE COALESCE(referee_id, 0) <> 2;
```
(An equivalent, more explicit form is `WHERE referee_id IS NULL OR referee_id <> 2`.)

## Complexity

- **Time:** O(N) – the query scans each row of the `Customer` table once.
- **Space:** O(1) – only constant extra space is used besides the output.

## Pros

- Very concise; a single predicate handles both conditions.
- Runs in a single pass over the table, optimal for large datasets.
- Works with standard SQL functions available in MySQL.

## Cons

- Relies on the assumption that `0` is never a valid `referee_id`. If `0` could appear, the `COALESCE` trick would produce incorrect results.
- The intent is less obvious than the explicit `IS NULL OR referee_id <> 2` formulation, which may affect readability.

## Edge cases

- All `referee_id` values are `2` → result set is empty.
- All `referee_id` values are `NULL` → all customer names are returned.
- Mixed `NULL`, `2`, and other ids → only names with `NULL` or ids ≠ 2 are returned.
- Empty `Customer` table → returns an empty result.
