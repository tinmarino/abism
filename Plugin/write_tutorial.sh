#!/bin/bash -i
title=$1 # title 
text=$2
clear

Title()
  {
NONE='\033[00m'
RED='\033[01;31m'
GREEN='\033[01;32m'
YELLOW='\033[01;33m'
PURPLE='\033[01;35m'
CYAN='\033[01;36m'
WHITE='\033[01;37m'
BOLD='\033[1m'
UNDERLINE='\033[4m'
  ast="************************************************"
  columnas=$(tput cols)
  y=$((($columnas-${#ast})/2))
  x=0
  
  tput clear
  tput cup $x $y
  echo "${ast}"
  echo ""
  
  y=$((($columnas-${#title})/2))
  x=1
  tput cup $x $y
  echo -e "${BOLD} ${title} ${NONE}"
  echo ""
  
  y=$((($columnas-${#ast})/2))
  x=2
  tput cup $x $y
  echo "${ast}"
  }

Text()
  {
  l=4
  c=5
  tput cup $l $c 
  echo "${text}"
  }
Title
Text
