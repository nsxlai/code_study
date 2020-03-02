# code_study
This repo is used as interview code_study


Mercurial rebase strategy:
[raylai@devvm452.ftw3 ~/fbsource/fbcode/havoc/autoval/tests/connect] hg sl
  @  bd6a8daf  101 seconds ago  raylai  feature/monkey_type* original
 /   Add monkey type flag in connecttest TARGET; experiemental
|
o  dab7edee  106 seconds ago  remote/master
.
o  88f7a309  83 minutes ago  remote/fbobjc/stable
.
o  d4c32cfd  Today at 10:00  remote/fbcode/warm
.
o  068ddd1d  Today at 09:36  remote/fbandroid/stable
.
o  fb634efd  Today at 09:08  remote/fbsource/stable
.
| o  eef42aa1  3 minutes ago  raylai
|/   Updating lib/test_base.py with type annotation using MonkeyType tool
|
o  16040b19  Wednesday at 09:37
|
~
hint[sl-short-headers]: unrelated public commits were collapsed - to see those details use --verbose
hint[hint-ack]: use 'hg hint --ack sl-short-headers' to silence these hints
[raylai@devvm452.ftw3 ~/fbsource/fbcode/havoc/autoval/tests/connect] hg rebase -s eef42aa1 -d bd6a8daf
rebasing eef42aa11827 "Updating lib/test_base.py with type annotation using MonkeyType tool"
eef42aa11827 -> c3d7758f0744 "Updating lib/test_base.py with type annotation ..."
[raylai@devvm452.ftw3 ~/fbsource/fbcode/havoc/autoval/tests/connect] hg sl
  o  c3d7758f (Backing up)  6 seconds ago  raylai
  |  Updating lib/test_base.py with type annotation using MonkeyType tool
  |
  @  bd6a8daf  101 seconds ago  raylai  feature/monkey_type* original
 /   Add monkey type flag in connecttest TARGET; experiemental
|
o  dab7edee  106 seconds ago  remote/master
.
o  88f7a309  85 minutes ago  remote/fbobjc/stable
.
o  d4c32cfd  Today at 10:00  remote/fbcode/warm
.
o  068ddd1d  Today at 09:36  remote/fbandroid/stable
.
o  fb634efd  Today at 09:08  remote/fbsource/stable
|
~
hint[sl-short-headers]: unrelated public commits were collapsed - to see those details use --verbose
hint[hint-ack]: use 'hg hint --ack sl-short-headers' to silence these hints
[raylai@devvm452.ftw3 ~/fbsource/fbcode/havoc/autoval/tests/connect]
