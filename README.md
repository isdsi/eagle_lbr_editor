# eagle_lbr_editor
editor using PyQt5 to edit an library file(*.lbr) for eagle cad

1. lbr file uses UNIX LF for line feed.
2. eagle cad makes backup file (*.l#1, *.l#2,...) when the user save the lbr file.
3. if you want to edit the attributes of all devices, you can use this.

usage:
1. open your lbr, sch, brd file.
2. open lbr_editor_qt.py. ( it needs pyqt5 )
3. open your file in the lbr_editor_qt.
4. edit the attribute.
5. click the save button in the lbr_editor_qt. (it will save "..._output.lbr")
6. click the change button in the lbr_editor_qt. 
7. check the attributes you changed in sch, brd file on eagle cad.

roadmap:
1. add an attribute for all devices.
2. delete an attribute for all devices.
3. make all devices have same attributes.