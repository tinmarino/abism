



def GetValueIP(event, destroy=True): # ImageParameter
    for i in G.image_parameter_list:
        vars(W.head)[i[1]] = float(vars(G.tkentry)[i[1]].get())
        # COLOR
        if vars(W.head)[i[1]] == i[2]:
            vars(G.tkentry)[i[1]]["bg"] = "#ff9090"
        else:
            vars(G.tkentry)[i[1]]["bg"] = "#ffffff"
        ResetLabel(expand=False)

