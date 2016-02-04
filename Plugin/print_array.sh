#!/bin/bash
# we take a array of columns separated by a "," and line by a \n
OIFS=$IFS
C=$(tput cols)
L=$(tput lines) 
size=5



##############
#1/ Read 2d array  
declare -A array2 
i=0  
while read line ; do 
  IFS="," ; array=( $line ) 
  j=0
  for column in ${array[@]} ; do 
     array2[$i,$j]="${column}"
     ((j++))
     done 
  ((i++))
  done <<< "${1}"


((cols=j-1));((rows=i-1))

##############
# 2/ print array 
for ((row=0; row<=rows; row++)); do
    for ((col=0; col<=cols; col++)); do
        #echo $row $col ${array2[$row,$col]}
        #echo -n  ${array2[$row,$col]}$'\t'
	stg="${array2[$row,$col]}"
	if [[ $col == 0 ]] ; then 
	   printf "%15s  " $stg 
	elif [[ $row == 0 ]]; then 
	   stg=${stg: ((size-1))} 
	   printf "%.${size}s  " .$stg
	else  # including the numbers 
	   printf "%.${size}s  " $stg
        fi 
    done
    echo 
    # pass line 
    #IFS=" " ; for tmp  in $(eval echo {1..$(tput cols)})  ; do echo -n  "_"; done;echo 

done


IFS=$OIFS
