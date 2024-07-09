Execution times of experiments with fixed-size datasets and increasing noise levels.

For each DC folder:

`explains:` obtained execution plans
<br>
`results:` results and measurement data

For each folder within `results`:

    A -> Q1
    B -> Q2
    C -> Q3
    D -> Q4
    E -> Q5
    F -> Q6

`insert_times.csv:` insert times of the dataset into the DBMS
<br>
`dc.dc:` executed DC
<br>
`search_times.csv:` average execution times (seconds) for each DBMS in each dataset (noise level)
<br>
`log:` checks or logs of the obtained results
```
For each log.csv:
- A,B,C:        number of violations detected
- D,E:          number of tuples participating in any violation
- F:            1 if detect any violation else 0
- NotSupport:   Does not accept the query
- NotRun:       Error on executing the query
- TimeLimitToExecQuery:     Exceeded execution time limit 
```