/* paramed.h  -- Parameter editor
 * $Id: paramed.h,v 1.4 2002/03/17 09:35:58 bitman Exp $
 * Copyright (C) 2001 Ryan Phillips <bitman@users.sourceforge.net>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 */

#ifndef __PARAMED_H
#define __PARAMED_H

#include "libzzt2/zzt.h"
#include "svector.h"
#include "dialog.h"

#include "display.h"


/* Direction flags */
#define DIR_NORTH 0x01
#define DIR_SOUTH 0x02
#define DIR_EAST  0x04
#define DIR_WEST  0x08

/* modifyparam(display, world, x, y)
 * Modify the parameter for the given tile
 */
void modifyparam(displaymethod * d, ZZTworld * w, int x, int y);

/* editprogram(display, param)
 * edit program in param p
 */
void editprogram(displaymethod * d, ZZTparam * p);

/* programtosvector(param, editwidth)
 * creates a string vector from the given param
 */
stringvector programtosvector(ZZTparam * p, int editwidth);

/* svectortoprogram(stringvector)
 * copies the contents of the given svector into a new
 * param. Only the program and length variables are used!
 */
ZZTparam svectortoprogram(stringvector sv);

/* getdirection(xstep, ystep)
 * Get a direction based on x and y step values
 */
int getdirection(char xstep, char ystep);

/* getxystep(xstep, ystep, dir)
 * Determines xstep and ystep from given direction
 */
void getxystep(char * xstep, char * ystep, int dir);

/* nextdirection(dir)
 * Returns the next direction after that given
 */
int nextdirection(int dir);

/* paramdatavaluestring(buffer, tile, which, world)
 * store to the buffer a string representing the
 * value of tile.param->data[which]
 */
char * paramdatavaluestring(char * buffer, ZZTtile tile, int which, ZZTworld * w);

/* buildparamdialog(world, x, y)
 * Builds and returns a param dialog based on the tile
 * at (x, y) in the given world
 */
dialog buildparamdialog(ZZTworld * w, int x, int y);

/* parameditoption(display, world, x, y, option)
 * Edit the params for the tile at (x, y) in
 * the context of the given option.
 * Returns true if change occured
 */
int parameditoption(displaymethod * d, ZZTworld * w, int x, int y, dialogComponent * opt);

/* paramdeltaoption(display, world, x, y, option, delta)
 * Increase/Decrease option by given delta amount.
 * Returns true if change occured
 */
int paramdeltaoption(displaymethod * d, ZZTworld * w, int x, int y, dialogComponent * opt, int delta);

/* tileinfo(display, world, x, y)
 * Display/edit info for the current tile
 */
void tileinfo(displaymethod * d, ZZTworld * w, int x, int y);

/* buildtileinfodialog(world, x, y)
 * Builds info for dialog at (x, y)
 */
dialog buildtileinfodialog(ZZTworld * w, int x, int y);

#endif