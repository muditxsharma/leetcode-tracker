# Classes With at Least 5 Students

- **Platform:** LeetCode
- **Difficulty:** Easy
- **Tags:** Database
- **Link:** https://leetcode.com/problems/classes-with-at-least-5-students/
- **Language (detected):** mysql
- **Runtime:** 319 ms
- **Memory:** 0B

## Problem (summary)

Table: Courses

+-------------+---------+
| Column Name | Type    |
+-------------+---------+
| student     | varchar |
| class       | varchar |
+-------------+---------+
(student, class) is the primary key (combination of columns with unique values) for this table.
Each row of this table indicates the name of a student and the class in which they are enrolled.

 

Write a solution to find all the classes that have at least five students.

Return the result table in any order.

The result format is in the following example.

 

Example 1:

Input: 
Courses table:
+---------+----------+
| student | class    |
+---------+----------+
| A       | Math     |
| B       | English  |
| C       | Math     |
| D       | Biology  |
| E       | Math     |
| F       | Computer |
| G       | Math     |
| H       | Math     |
| I       | Math     |
+---------+----------+
Output: 
+---------+
| class   |
+---------+
| Math    |
+---------+
Explanation: 
- Math has 6 students, so we include it.
- English has 1 student, so we do not include it.
- Biology has 1 student, so we do not include it.
- Computer has 1 student, so we do not include it.

## Approach

**Approach**

1. **Group by `class`** – Use `GROUP BY class` to collect all rows belonging to the same class.
2. **Count students** – Apply `COUNT(student)` (or `COUNT(DISTINCT student)` if the primary‑key guarantee is ignored) to obtain the number of enrolled students per class.
3. **Filter with HAVING** – Keep only those groups where the count is **≥ 5** using a `HAVING` clause.
4. **Select the class name** – Return the `class` column from the filtered groups.

The final query is a single statement:
```sql
SELECT class
FROM Courses
GROUP BY class
HAVING COUNT(student) >= 5;
```

## Complexity

- **Time:** O(N) – each row of the `Courses` table is examined once during the aggregation, where N is the number of rows.
- **Space:** O(K) – additional space for the hash map of groups, where K is the number of distinct classes (K ≤ N).

## Pros

- Very concise – a single SQL statement solves the problem.
- Leverages built‑in aggregation and filtering, so the database engine handles all heavy lifting efficiently.
- Works for any size of input as long as the table fits in the DB engine’s memory/processing limits.

## Cons

- Relies on the guarantee that `(student, class)` is unique; otherwise duplicate rows would inflate the count – you would need `COUNT(DISTINCT student)`.
- If the table is extremely large and not indexed on `class`, the aggregation may require a full table scan.

## Edge cases

- A class with exactly 5 students should be included (≥ 5).
- No class reaches 5 students – the query returns an empty result set.
- The `Courses` table is empty – also returns an empty result set.
- All rows belong to the same class – the query returns that single class if its count ≥ 5.
