#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  surlog.py
#  
#  Copyright 2012 Giorgio Gilestro <gg@kinsey>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

from surgeryLogger import surgeries, users
import argparse, os

def main():
    parser = argparse.ArgumentParser(prog='PROG')
    
    parser.add_argument('--add', type=int, help='Add a new surgery')
    parser.add_argument('--close', nargs='+', help='Close the surgery')
    
    parser.add_parser('edit', help='Edit an existing surgery')
    parser.add_argument('--item', nargs=2)
    
    parser.add_argument('--list', help='List all surgeries')
    
    

if __name__ == '__main__':
    main()

