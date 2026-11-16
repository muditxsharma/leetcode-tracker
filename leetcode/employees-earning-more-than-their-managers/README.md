# Employees Earning More Than Their Managers

- **Platform:** LeetCode
- **Difficulty:** Easy
- **Tags:** Database
- **Link:** https://leetcode.com/problems/employees-earning-more-than-their-managers/
- **Language (detected):** mysql
- **Runtime:** 358 ms
- **Memory:** 0B

## Problem (summary)

Table: Employee

+-------------+---------+
| Column Name | Type    |
+-------------+---------+
| id          | int     |
| name        | varchar |
| salary      | int     |
| managerId   | int     |
+-------------+---------+
id is the primary key (column with unique values) for this table.
Each row of this table indicates the ID of an employee, their name, salary, and the ID of their manager.

 

Write a solution to find the employees who earn more than their managers.

Return the result table in any order.

The result format is in the following example.

 

Example 1:

Input: 
Employee table:
+----+-------+--------+-----------+
| id | name  | salary | managerId |
+----+-------+--------+-----------+
| 1  | Joe   | 70000  | 3         |
| 2  | Henry | 80000  | 4         |
| 3  | Sam   | 60000  | Null      |
| 4  | Max   | 90000  | Null      |
+----+-------+--------+-----------+
Output: 
+----------+
| Employee |
+----------+
| Joe      |
+----------+
Explanation: Joe is the only employee who earns more than his manager.

## Approach

The query uses a **self‑join** on the `Employee` table. Each employee row `E` is left‑joined to its manager row `M` by matching `E.managerId = M.id`. After the join, we simply filter rows where the employee’s salary is greater than the manager’s salary (`E.salary > M.salary`). The selected column is the employee’s name, aliased as `Employee`. This directly yields all employees who earn more than their direct manager.

```sql
SELECT E.name AS Employee
FROM Employee E
LEFT JOIN Employee M ON E.managerId = M.id
WHERE E.salary > M.salary;
```

## Complexity

- **Time:** O(N) – the self‑join scans each row once (plus index look‑ups), effectively linear in the number of employees.
- **Space:** O(N) – additional space is needed for the join result and the output rows.

## Pros

- Very concise – a single SQL statement.
- Leverages relational nature of the data; no procedural logic needed.
- Handles `NULL` managerId automatically (they are excluded because `M.salary` is NULL).

## Cons

- Relies on the existence of an index on `id`/`managerId` for optimal performance; otherwise the join could be costly on very large tables.
- Only compares direct manager‑employee pairs; does not consider indirect hierarchy (which is not required by the problem).
- If multiple employees share the same name, the result may contain duplicates (the problem expects names only).

## Edge cases

- Employees with `managerId` = NULL – they should not appear in the result.
- Employees whose salary equals their manager’s salary – they are excluded because the condition is strict (`>`).
- Managers who themselves have a manager – each employee is evaluated only against their immediate manager.
- Empty `Employee` table – query returns an empty result set.
