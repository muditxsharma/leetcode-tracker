# Customer Placing the Largest Number of Orders

- **Platform:** LeetCode
- **Difficulty:** Easy
- **Tags:** Database
- **Link:** https://leetcode.com/problems/customer-placing-the-largest-number-of-orders/
- **Language (detected):** mysql
- **Runtime:** 498 ms
- **Memory:** 0B

## Problem (summary)

Table: Orders

+-----------------+----------+
| Column Name     | Type     |
+-----------------+----------+
| order_number    | int      |
| customer_number | int      |
+-----------------+----------+
order_number is the primary key (column with unique values) for this table.
This table contains information about the order ID and the customer ID.

 

Write a solution to find the customer_number for the customer who has placed the largest number of orders.

The test cases are generated so that exactly one customer will have placed more orders than any other customer.

The result format is in the following example.

 

Example 1:

Input: 
Orders table:
+--------------+-----------------+
| order_number | customer_number |
+--------------+-----------------+
| 1            | 1               |
| 2            | 2               |
| 3            | 3               |
| 4            | 3               |
+--------------+-----------------+
Output: 
+-----------------+
| customer_number |
+-----------------+
| 3               |
+-----------------+
Explanation: 
The customer with number 3 has two orders, which is greater than either customer 1 or 2 because each of them only has one order. 
So the r

(Truncated.)

## Approach

**Approach**

1. **Group orders by `customer_number`** – use `GROUP BY` to aggregate all rows belonging to the same customer.
2. **Count orders per customer** – `COUNT(order_number)` gives the number of orders each customer placed.
3. **Sort by the count in descending order** – `ORDER BY COUNT(order_number) DESC` puts the customer with the most orders at the top.
4. **Return the top row** – `LIMIT 1` selects the single `customer_number` that has the highest order count (the problem guarantees a unique maximum).

The query is a single statement that leverages SQL’s built‑in aggregation and ordering capabilities.

**Why it works**
- `GROUP BY` collapses all rows of a customer into one group.
- `COUNT` computes the size of each group.
- Ordering by that size and limiting to one yields the customer with the maximum count.

**Follow‑up handling of ties**
If ties need to be reported, replace `LIMIT 1` with a `HAVING` clause that matches the maximum count, e.g.,
```sql
SELECT customer_number
FROM Orders
GROUP BY customer_number
HAVING COUNT(*) = (
    SELECT MAX(cnt) FROM (
        SELECT COUNT(*) AS cnt FROM Orders GROUP BY customer_number
    ) t
);
```

## Complexity

- **Time:** O(N log K) where N is the number of rows in `Orders` and K is the number of distinct customers (grouping is O(N), sorting the K groups is O(K log K))
- **Space:** O(K) for the intermediate groups (one entry per distinct customer)

## Pros

- Very concise – a single SQL statement
- Uses standard SQL constructs, portable across DBMS
- Leverages built‑in aggregation, no procedural code needed
- Efficient for typical data sizes

## Cons

- Sorting all groups can be slower than a direct MAX‑based subquery for very large K
- `LIMIT 1` hides ties – only works because the problem guarantees a unique maximum
- Relies on the database’s query optimizer; performance may vary with indexes

## Edge cases

- Table contains only one row – query correctly returns that customer
- All customers have the same number of orders – query returns an arbitrary one (problem guarantees uniqueness, otherwise use a HAVING clause)
- Very large number of distinct customers – memory usage grows with O(K) for the grouping step
