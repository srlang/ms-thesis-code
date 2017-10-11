#ifndef __UTILS_H
#define __UTILS_H

#include <stdio.h>

#define DEBUG	1

#ifdef DEBUG
	#if DEBUG
	#define PD(...)		fprintf(stderr, __VA_ARGS__)
	#else
	#define PD(...)		// do nothing
	#endif
#else
	#define PD(...)		// do nothing
#endif

#endif /* __UTILS_H */
