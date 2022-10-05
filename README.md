# commitdate
## commitdate.py
This is a simple script that aims dumping the git commands you would do, to 
make a local repository, into a git repo.
## Running commitdate.py
This works as follow.
In Linux, you run,
1. `find * -type f -printf "%TY-%Tm-%Td %TH:%TM:00. %p\n"`
1. and you can combine this command with
   + `... | python3 commitdate.py`
The script assumes you have listed all the files in your repository you need.
- It gathers commits by date, at the same day.
- It is quite simplistic, but it helps in vast majority of the cases.
