/* kevedit.h    -- Editor definitions
 * $Id: kevedit.h,v 1.17 2002/09/13 17:51:20 bitman Exp $
 * Copyright (C) 2000 Kev Vance <kev@kvance.com>
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

#ifndef _KEVEDIT_H
#define _KEVEDIT_H 1

#include "libzzt2/zzt.h"
#include "display.h"
#include "patbuffer.h"
#include "colours.h"
#include "selection.h"

/* Update Flags */
#define UD_NONE         0x00  /* Nothing at all */
#define UD_BOARD        0x01  /* The entire board */
#define UD_PANEL        0x02  /* The entire panel */
#define UD_PANEL_TOP    0x04  /* Top area of the panel */
#define UD_PANEL_MIDDLE 0x08  /* Middle area of the panel */
#define UD_PANEL_BOTTOM 0x10  /* Bottom area of the panel */
#define UD_CURSOR       (0x20 | UD_PANEL_TOP)  /* The cursor spot and panel indicator */
#define UD_SPOT         0x40            /* The spot around the cursor */
#define UD_BOARDTITLE   0x80            /* Title of current board should be drawn */
#define UD_WORLDTITLE   0x100           /* Title of the world has changed */
#define UD_OBJCOUNT     UD_PANEL_TOP    /* Object count */
#define UD_WORLDTITLE   UD_PANEL_TOP    /* World Title */
#define UD_TEXTMODE     UD_PANEL_MIDDLE /* Text entry mode */
#define UD_DRAWMODE     UD_PANEL_MIDDLE /* Draw mode */
#define UD_BLINKMODE    UD_PANEL_BOTTOM /* Blink mode */
#define UD_PATTERNS     UD_PANEL_BOTTOM /* Pattern selector, backbuffer, & aqu mode */
#define UD_COLOR        UD_PANEL_BOTTOM /* Color selectors */
#define UD_COLORMODE    UD_PANEL_BOTTOM /* defc */
#define UD_ALL          (UD_BOARD | UD_PANEL)  /* Everything */

/* Aquire modes */
#define AQUMODE_OFF       0
#define AQUMODE_NORESIZE  1  /* Don't resize the backbuffer */
#define AQUMODE_RESIZE    2  /* Grow backbuffer to hold new tiles */

/* Selection mode */
#define SELECT_OFF     0  /* Select mode is off */
#define SELECT_ON      1  /* An area is selected */
#define SELECT_BLOCK   2  /* Select by block */
#define SELECT_CLEAR  -1  /* Selection must be cleared */


typedef struct kevoptions {
	/* Kevedit options */
	/* TODO: should be loaded from config file eventually */
	int colorStandardPatterns;
	int vimovement;

} kevoptions;

typedef struct keveditor {
	ZZTworld      * myworld;   /* The world */
	displaymethod * mydisplay; /* Display method */
	char          * datapath;  /* Default location of data files */
	/* Help system and copy/paste registers also belong here,
	 * rather than being globally accessible. */

	/* Cursor position */
	int cursorx, cursory;

	/* Control flags */
	int updateflags;
	int quitflag;

	/* Most recent keypress */
	int key;

	/* Mode toggles */
	int drawmode;
	int gradmode;
	int aqumode;
	int textentrymode;
	int defcmode;

	/* Current colour */
	textcolor color;

	/* Backbuffers */
	backbuffers buffers;

	/* Selection mode */
	int selectmode;
	int selx, sely;
	selection sel;

	/* Options */
	kevoptions options;

} keveditor;

/* Create a KevEdit editor */
keveditor * createkeveditor(ZZTworld * myworld, displaymethod * mydisplay, char * datapath);

/* Free a kevedit editor */
void deletekeveditor(keveditor * myeditor);

/* Run the editor */
void kevedit(keveditor * myeditor);

/* The all-powerful min/max macros */
#define min(a, b) ((a) < (b) ? (a) : (b))
#define max(a, b) ((a) > (b) ? (a) : (b))

#endif				/* _KEVEDIT_H */

