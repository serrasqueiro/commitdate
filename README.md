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
## Using commitdate.py scratch
Example for `beautifulsoup4-4.11.1`:
1. `tar xvfz /tmp/beautifulsoup4-4.11.1.tar.gz`
1. `cd beautifulsoup4-4.11.1`
1. Ensure no .git directory there: `rm -rf .git`
1. Initialize this repo, at its base directory: `git init`
1. `find * -type f -printf "%TY-%Tm-%Td %TH:%TM:00. %p\n" | python3 /tmp/commitdate.py > ~/importer`
1. `chmod 750 ~/importer`
1. `~/importer`
You can navigate using `git log`, and verify the corresponding commits are done.
