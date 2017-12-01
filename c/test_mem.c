#include <stdlib.h>

#include "db_populate.h"
#include "utils.h"

int main(void) {
	// test to make sure memory allocation is serial so that all of my
	// assumptions of contiguous memory don't  screw up my data later and
	// render a 23-day computation useless (worst of all unbeknownst to me)
	
	printf("Starting....\n");
	
	KeepToss * kts = (KeepToss *) calloc(10, sizeof(KeepToss));
	for (int i = 0; i < 10; i++) {
		for (int j = 0; j < 9; j++) {
			kts[i].keep[j] = j;
		}
	}

	for (int i = 0; i < 10; i++) {
		for (int j = 0; j < 4; j++)
			ASSERT_EQ(kts[i].keep[j], j, "keep differs at index %d\n", j);
		for (int j = 0; j < 2; j++)
			ASSERT_EQ(kts[i].toss[j], j+3, "toss differs at index %d\n", j);
		for (int j = 0; j < 2; j++)
			ASSERT_EQ(kts[i].tosd[j], j+5, "tosd differs at index %d\n", j);
		ASSERT_EQ(kts[i].cut, 7, "cut card differs\n");
	}

	printf("...done\n");
}
