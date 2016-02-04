try : from Tkinter import *
except  : from tkinter import *
import ttk





lst =[
       [1, 
         [ 12, ["ererere",
                "zezezez",
                "ezez", 
               ],
         ],
         [13 ],
         [14 ] ,
         
      ],
      [2],
      ["azeazeaz",
        ["azeaz",[33,
                  34,
                  35,
                 ],
        ]
      ]
    ]


def List2Tree(lst,parent) : # Tree should be a global 
  for i in lst : 
    id = tree.insert(parent,"end",text= i[0])
    #List2Tree(i[1],id,tree) 

## DIRECTORY 1
#t.insert("",0,"dir1",text="directory 1")
#t.insert("dir1","end","dir 1",text="file 1 1") #,values=("file 1 A","file 1 B"))
#
## DIRECTORY 2 
#id=t.insert("","end","dir2",text="directory 2")
#t.insert("dir2","end",text="dir 2")#,values=("file 2 A","file 2 B"))
#id2= t.insert(id,"end",text="nested d") 
#t.insert(id2,"end",text="noauerpazea ")#,values=("val 1 ","val 2"))

parent=Tk()
tree=ttk.Treeview(parent)

List2Tree(lst,parent) 

tree.tag_configure("ttk")
tree.pack(side=BOTTOM,fill=BOTH,expand=True)
parent.mainloop()


