# (c)2022  Henrique Moreira

""" commitdate.py - outputs git commands from textual dates
"""

# pylint: disable=missing-function-docstring

import sys
import datetime
import os.path

DEF_MESSAGE = "Committed $$"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S" + "."

def main():
    code = runner(sys.argv[1:])
    if code is None:
        print(f"""Usage:
{__file__} [textual-dates-input]

Outputs git commands for committing with corresponding dates.
Default message is:
    {DEF_MESSAGE}

where $$ embodies the files committed.
""")

def runner(args):
    """ Parse args and run! """
    param = args
    if param:
        if param[0].startswith("-"):
            return None
    else:
        param = ["--stdin"]
    if len(param) > 1:
        print("Too many params.", end="\n\n")
        return None
    opts = {
        "verbose": 0,
        "msg": DEF_MESSAGE,
        "dirs": "short",
    }
    return do_script(param, opts)

def do_script(param, opts:dict):
    verbose = opts["verbose"]
    inp = param[0]
    if inp == "--stdin":
        fdin = sys.stdin
    else:
        fdin = open(inp, "r", encoding="ascii")
    lines = [line.rstrip() for line in fdin.readlines()]
    works = process(lines, sys.stderr)
    # Gather commits
    atcommit = [0] * len(works)
    commits, dates = gather_commits(works, atcommit)
    reorganize(commits, opts)
    # Dump timestamps
    for idx, tup in enumerate(works):
        commit_nr = atcommit[idx]
        dttm, path, _ = tup
        print(f"# commit#{commit_nr}:", dttm, path)
        dates[commit_nr].append(path)
    if verbose > 0:
        print(">>>\n" + '\n'.join(['+'.join(item) for item in commits]), end="\n<<<\n\n")
    dump_finally(sys.stdout, (commits, dates), opts)
    return 0

def dump_finally(out, infos, opts):
    """ Finally, the output of git commands! """
    base = opts["msg"]
    commits, dates = infos
    for idx, commit in enumerate(commits, 1):
        dirs = commit[0]
        rest = commit[1:]
        mdate = dates[idx][0][1]
        assert '"' not in mdate
        files = dates[idx][1:]
        #print("\nCOMMIT#", idx, "at:", mdate, commit, end="\n\n")
        for path in files:
            out.write(f"git add {path}\n")
        if dirs:
            msg = base.replace("$$", dirs)
        else:
            msg = ""
        msg = msg.replace('"', "")
        s_rest = ""
        for name in rest:
            if len(s_rest) + len(name) > 76:
                s_rest += " ..."
                break
            if s_rest:
                s_rest += ", "
            else:
                s_rest += "- " if msg else ""
            s_rest += name
        if s_rest:
            s_rest = s_rest.replace('"', "")
            s_rest = f' -m "{s_rest}"'
        if msg:
            p_msg = f'-m "{msg}"'
        else:
            p_msg = ""
        s_msg = f'git commit --date="{mdate}"{p_msg}{s_rest}\n'
        out.write(s_msg)
    return True

def gather_commits(works, atcommit):
    """ Fills-in 'atcommit' indexes, based on input 'works' """
    commits = []
    dates = {}
    last, new = 0, []
    dttm = None
    for idx, tup in enumerate(works):
        dttm, path, base = tup
        ydoy = to_ydoy(dttm)
        if ydoy == last:
            new.append([path, base])
        else:
            if new:
                commits.append(new)
            new = [[path, base]]
        last = ydoy
        commit_nr = len(commits) + 1
        atcommit[idx] = commit_nr
        dates[commit_nr] = [(dttm, commit_date_str(dttm))]
    if new:
        assert dttm is not None
        commits.append(new)
    return commits, dates

def reorganize(commits, opts:dict):
    """ Not really a re-organization, but rather re-build messaging
    """
    short_dirs = opts["dirs"] == "short"
    assert commits
    for idx, commit in enumerate(commits):
        new, dirs = [], []
        #print("idx-0based:", idx, "; commit:", commit)
        for item in commit:
            new.append(item[1])
            adir = os.path.dirname(item[0])
            if adir:
                dirs.append(adir.replace("\\", "/") + "/")
        asort = sorted(set(new))
        dirs = sorted(set(dirs))
        if short_dirs:
            # Simplifying...
            dirs = simpler_subdirs(dirs)
        # remaining follows...
        if len(dirs) > 1:
            s_dir = ''.join([sdir + " " for sdir in dirs]) + ":"
        else:
            s_dir = ''
        commits[idx] = [s_dir] + asort
    return True

def simpler_subdirs(dirs):
    # Remove dirs that are sub-strings of others
    rest = []
    for idx, adir in enumerate(dirs):
        is_sub = False
        for this, searched in enumerate(dirs):
            if idx == this:
                continue
            if searched.startswith(adir):
                is_sub = True
                break
        if is_sub:
            continue
        rest.append(adir)
    return rest

def process(lines:list, err):
    """ Returns an ordered list of tuples
    """
    items = []
    for idx, item in enumerate(lines, 1):
        if not item or item.startswith("#"):
            continue
        trip = [this for this in item.split(" ", maxsplit=2) if this.strip()]
        if len(trip) != 3:
            if err:
                err.write(f"Invalid line {idx} (#{len(trip)}): '{item}'\n")
            return []
        adate = " ".join(trip[:2])
        #print(adate, ";", trip)
        dttm = datetime.datetime.strptime(adate, DATE_FORMAT)
        path = trip[-1]
        info = os.path.basename(path)
        items.append((dttm, path, info))
    ordered = sorted(items, key=lambda x: x[0])
    return ordered

def to_ydoy(dttm):
    """ Returns the year * 1000, plus day of the year (1..366);
    example: 1st January 2022, is 2022001
    """
    return dttm.year * (10 ** 3) + dttm.timetuple().tm_yday

def commit_date_str(dttm):
    return f"{dttm}"

if __name__ == "__main__":
    main()
