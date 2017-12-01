#ifndef __UTILS_H
#define __UTILS_H

#include <stdio.h>

#define DEBUG	1

/*
#ifdef DEBUG
	#if DEBUG
	#define PD(...)		fprintf(stderr, __VA_ARGS__)
	#else
	#define PD(...)		// do nothing
	#endif
#else
*/
	#define PD(...)		// do nothing
/*
#endif
*/

#define MAX(x,y)		((x) > (y) ? (x) : (y))

#define ASSERT_EQ(x,y,...)	do {\
		if (x != y) {\
			PD(__VA_ARGS__);\
		}\
	} while (0);

#endif /* __UTILS_H */
